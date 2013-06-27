from functools import partial
import glob
import json
import logging
import os
import hashlib
import mimetypes
import pprint
import requests
from daf_fruit_dist.checksums import Checksums
from daf_fruit_dist.file_management import get_file_digests


_HEADER_USER_AGENT = 'User-Agent'
_HEADER_MD5_CHECKSUM = 'X-Checksum-Md5'
_HEADER_SHA1_CHECKSUM = 'X-Checksum-Sha1'
_HEADER_CONTENT_TYPE = 'Content-Type'
_HEADER_CONTENT_ENCODING = 'Content-Encoding'

_CONTENT_TYPE_PROMOTION_REQUEST = (
    'application/vnd.org.jfrog.artifactory.build.PromotionRequest+json')

_CONTENT_TYPE_PUBLISH_BUILD_INFO = (
    'application/vnd.org.jfrog.artifactory+json')


def deploy_file(
        repo_base_url,
        repo_push_id,
        path,
        filename,
        attributes=None,
        username=None,
        password=None,
        verify_cert=True):
    """
    Deploy the file to the /path/ directory at the given URL. A
    dictionary (or pre-formatted string) of attributes may also be
    supplied.
    """

    def store_hashes_in_headers(headers):
        md5, sha1 = get_file_digests(
            filename,
            digests=(hashlib.md5(), hashlib.sha1()))

        headers[_HEADER_MD5_CHECKSUM] = md5.hexdigest()
        headers[_HEADER_SHA1_CHECKSUM] = sha1.hexdigest()

    def store_mimetypes_in_headers(headers):
        content_type, content_enc = mimetypes.guess_type(filename)

        if content_type:
            headers[_HEADER_CONTENT_TYPE] = content_type
        if content_enc:
            headers[_HEADER_CONTENT_ENCODING] = content_enc

    def generate_uri():
        basename = os.path.basename(filename)
        norm_path = _normalize_path(path)
        uri = '{url}/{repo_push_id}/{path}/{basename}'.format(
            url=repo_base_url,
            repo_push_id=repo_push_id,
            path=norm_path,
            basename=basename)

        if attributes:
            if isinstance(attributes, dict):
                uri += ';' + ';'.join(
                    '{}={}'.format(k, v) for k, v in attributes.iteritems())
            elif isinstance(attributes, basestring):
                uri += ';' + attributes
            else:
                raise TypeError(
                    '"attributes" must be either a dictionary or a pre-'
                    'formatted string of "key1=value1;key2=value2" pairs')
        return uri

    def upload_file(deploy_uri):
        logging.info('Deploying: ' + deploy_uri)

        auth = (username, password) if (username or password) else None

        with open(filename, 'rb') as f:
            response = requests.put(
                deploy_uri,
                data=f,
                auth=auth,
                headers=headers,
                verify=verify_cert)

            _log_response(response)

    headers = _make_headers()

    store_hashes_in_headers(headers)
    store_mimetypes_in_headers(headers)

    upload_file(generate_uri())


def deploy_globbed_files(
        repo_base_url,
        repo_push_id,
        path,
        glob_patterns,
        attributes=None,
        username=None,
        password=None,
        verify_cert=True):
    """
    Like deploy_file, except this function takes a list of globbing
    patterns. All files (NOT directories) matched by these patterns are
    deployed to the server.
    """
    logging.debug("Entering deploy_globbed_files with:")
    logging.debug("   repo_base_url: {}".format(repo_base_url))
    logging.debug("   repo_push_id: {}".format(repo_push_id))
    logging.debug("   path: {}".format(path))
    logging.debug("   glob_patterns: {}".format(glob_patterns))

    # Create a version of deploy_file() with every field filled out
    # except for filename.
    deploy = partial(
        deploy_file,
        repo_base_url=repo_base_url,
        repo_push_id=repo_push_id,
        path=path,
        attributes=attributes,
        username=username,
        password=password,
        verify_cert=verify_cert)

    # Set of all files being uploaded. Note that a set is being used
    # here instead of a list so that files matched by more than one
    # globbing pattern are only uploaded once.
    filenames = set()

    for pattern in glob_patterns:
        filenames.update(filter(os.path.isfile, glob.glob(pattern)))

    logging.debug("Found filenames: {}".format(", ".join(filenames)))

    for f in filenames:
        deploy(filename=f)

    return filenames


def build_promote(
        username,
        password,
        repo_base_url,
        build_name,
        build_number,
        promotion_request,
        verify_cert=True):

    uri = '{url}/api/build/promote/{build_name}/{build_number}'.format(
        url=repo_base_url,
        build_name=build_name,
        build_number=build_number)

    json_data = promotion_request.as_json_data
    json_to_put_on_wire = json.dumps(json_data, sort_keys=True)

    auth = _make_auth(username, password)

    headers = _make_headers()
    headers[_HEADER_CONTENT_TYPE] = _CONTENT_TYPE_PROMOTION_REQUEST

    put_req = requests.post(
        uri,
        data=json_to_put_on_wire,
        headers=headers,
        auth=auth,
        verify=verify_cert)

    _log_response(put_req)
    put_req.raise_for_status()

    response_json = put_req.json()

    return response_json


def publish_build_info(
        username,
        password,
        repo_base_url,
        build_info,
        verify_cert=True):

    json_data = build_info.as_json_data
    json_to_put_on_wire = json.dumps(json_data, sort_keys=True)

    uri = '{url}/api/build'.format(url=repo_base_url)
    auth = _make_auth(username, password)

    headers = _make_headers()
    headers[_HEADER_CONTENT_TYPE] = _CONTENT_TYPE_PUBLISH_BUILD_INFO

    put_req = requests.put(
        uri,
        data=json_to_put_on_wire,
        headers=headers,
        auth=auth,
        verify=verify_cert)

    _log_response(response=put_req)

    put_req.raise_for_status()


def determine_checksums(
        username,
        password,
        repo_base_url,
        repo_pull_id,
        file_path,
        verify_cert=True):

    uri = '{url}/api/storage/{repo_pull_id}/{file_path}'.format(
        url=repo_base_url,
        repo_pull_id=repo_pull_id,
        file_path=file_path)

    auth = _make_auth(username, password)

    get_response = requests.get(
        uri,
        headers=_make_headers(),
        auth=auth,
        verify=verify_cert)

    get_response.raise_for_status()
    response_json = get_response.json()

    if 'checksums' in response_json:
        checksum_data = response_json['checksums']
        md5 = checksum_data.get('md5', None)
        sha1 = checksum_data.get('sha1', None)
    else:
        raise RuntimeError(
            "Artifact found in Artifactory but no checksums were available.")

    return Checksums(sha1=sha1, md5=md5)


def _normalize_path(path):
    return path.strip('/')


def _make_auth(username=None, password=None):
    return (username, password) if (username or password) else None


def _make_headers():
    return {_HEADER_USER_AGENT: 'FruitDist/1.0'}


def _log_response(response):
    _log_data_structure('response_headers', response.headers)

    try:
        _log_data_structure('response_json', response.json())
    except StandardError:
        response_text = getattr(response, 'text', None)
        if response_text:
            logging.debug('response_text: {}'.format(response_text))


def _log_data_structure(title, data_structure):
    unindented = pprint.pformat(data_structure)
    shifted = '\n   '.join(unindented.splitlines())
    log_msg = '{}:\n   {}'.format(title, shifted)
    logging.debug(log_msg)
