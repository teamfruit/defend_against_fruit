import subprocess
import requests
import sys
from functools import partial
from nose.tools import eq_, with_setup
from pypi_redirect.server_app import index_parser
from _artifactory_test_helper import ArtifactoryTestHelper
from _proxy_test_helper import ProxyTestHelper
from _utils import assert_services_up


def _find_all_links(html_root):
    return html_root.xpath(".//a")


def _assert_sphinx_packages(listed_packages):
    assert 'Sphinx-1.1-py2.7.egg' in listed_packages
    assert 'Sphinx-1.1-py2.7.egg.md5' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz.md5' in listed_packages


def _validate_content_type(expected_type, result):
    eq_(result.headers['Content-Type'], expected_type)


def _validate_content_length(expected_length, result):
    eq_(int(result.headers['content-length']), expected_length)


def _validate_md5(expected_md5, result):
    eq_(result.headers['x-checksum-md5'], expected_md5)


def _validate_text(expected_text, result):
    eq_(result.text, expected_text)


def _validate_404(result):
    eq_(result.status_code, 404)


def _get_from_artif_and_validate(package, filename, validate_fn_list):
    result = fixture.get_artif_repo_url(
        path='python/{}/{}'.format(package, filename))

    for v in validate_fn_list:
        v(result=result)


def _get_sphinx_from_artif_and_validate(
        checksum_ext='',
        expect_md5_not_found=False,
        lowercase_package=False):

    package = 'sphinx' if lowercase_package else 'Sphinx'
    filename = 'Sphinx-1.1.3.tar.gz' + checksum_ext
    expected_checksum = '8f55a6d4f87fc6d528120c5d1f983e98'

    validators = {
        # Non-checksum file validators
        '': (
            partial(_validate_content_length, 2632059),
            partial(_validate_md5, expected_checksum),
        ),

        # MD5 validators
        '.md5': (
            _validate_404,
        ) if expect_md5_not_found else (
            partial(_validate_text, expected_checksum),
            partial(_validate_content_type, 'application/x-checksum'),
        ),

        # SHA1 validators
        '.sha1': (
            _validate_404,
        ),
    }

    _get_from_artif_and_validate(
        package=package,
        filename=filename,
        validate_fn_list=validators[checksum_ext])


def _get_and_validate_files(get_and_validate_fn):
    ### 1. Package not cached.

    # a. Verify that getting the MD5 fails before the package is requested.
    get_and_validate_fn(checksum_ext='.md5', expect_md5_not_found=True)

    # b. Verify that getting the SHA1 fails before the package is requested.
    get_and_validate_fn(checksum_ext='.sha1')

    # c. Request package to cache it.
    get_and_validate_fn()

    ### 2. Package cached.

    # a. Verify that getting the MD5 succeeds after the package is cached.
    get_and_validate_fn(checksum_ext='.md5')

    # b. Verify that getting the SHA1 *still* fails after the package is
    #    cached (the proxy is not returning an SHA1 checksum).
    get_and_validate_fn(checksum_ext='.sha1')

    # c. Get the cached package again and verify that it still looks the same.
    get_and_validate_fn()


class Fixture(object):
    def __init__(
            self,
            artif_base_url,
            pypi_repo_id,
            proxy_base_url,
            clean_cache_auth):

        self.__artif_base_url = artif_base_url.strip('/')
        self.__pypi_repo_id = pypi_repo_id.strip('/')
        self.__proxy_base_url = proxy_base_url.strip('/')

        self.__artif_test_helper = ArtifactoryTestHelper(
            base_url=artif_base_url,
            pypi_repo_id=pypi_repo_id,
            clean_credentials=clean_cache_auth)

        self.__proxy_test_helper = ProxyTestHelper(
            base_url=proxy_base_url)

    def flush_caches(self):
        self.__artif_test_helper.clean_pypi_repo()

    #TODO: move to ArtifactoryTestHelper (put guts in util)
    def get_artif_repo_url(self, path='', only_headers=False):
        url = '/'.join((
            self.__artif_base_url,
            self.__pypi_repo_id,
            path.lstrip('/')))
        result = requests.head(url) if only_headers else requests.get(url)
        return result

    #TODO: move to ArtifactoryTestHelper (put guts in util?)
    def parse_artif_listing(self, path=''):
        #TODO: Somehow reuse get_artif_repo_url
        url = '/'.join((
            self.__artif_base_url,
            self.__pypi_repo_id,
            path.lstrip('/')))
        result = requests.get(url)
        result.raise_for_status()

        html_str = result.text

        # Our index_parser.parse is very well unit-tested.
        rows = index_parser.parse(
            base_url=url,
            package_path='',
            html_str=html_str,
            strict_html=False,
            find_links_fn=_find_all_links)

        return tuple(rows.iterkeys())

    #TODO: Move to proxy_test_helper (put guts in util)
    def get_proxy_url(self, path=''):
        url = '/'.join((self.__proxy_base_url, path.lstrip('/')))
        result = requests.get(url)
        return result

    def setup(self):
        self.proxy_process = subprocess.Popen([
            sys.executable, '-m', 'pypi_redirect'])

        assert_services_up(services=(
            self.__artif_test_helper,
            self.__proxy_test_helper))

        # These tests assume nothing is cached in Artifactory.
        self.flush_caches()

    def teardown(self):
        self.proxy_process.terminate()


fixture = Fixture(
    artif_base_url='http://localhost:8081/artifactory',
    pypi_repo_id='pypi-remote',
    proxy_base_url='http://localhost:9292',
    clean_cache_auth=('admin', 'password'))


def setup_module():
    fixture.setup()


def teardown_module():
    fixture.teardown()


def artif_root_test():
    actual_result = fixture.parse_artif_listing()
    expected_result = ('python/',)
    eq_(actual_result, expected_result)


def artif_pypi_root_no_slash_test():
    actual_result = fixture.get_artif_repo_url(path='python')
    eq_(actual_result.status_code, 404)


def artif_pypi_root_test():
    actual_result = fixture.get_artif_repo_url(path='python/')
    eq_(actual_result.status_code, 404)


def artif_sphinx_no_slash_test():
    actual_result = fixture.get_artif_repo_url(path='python/Sphinx')
    eq_(actual_result.status_code, 404)


def artif_lowercase_sphinx_no_slash_test():
    actual_result = fixture.get_artif_repo_url(path='python/sphinx')
    eq_(actual_result.status_code, 404)


def artif_sphinx_test():
    actual_result = fixture.parse_artif_listing(path='python/Sphinx/')
    _assert_sphinx_packages(actual_result)


def artif_lowercase_sphinx_test():
    actual_result = fixture.parse_artif_listing(path='python/sphinx/')
    _assert_sphinx_packages(actual_result)


@with_setup(teardown=fixture.flush_caches)
def get_sphinx_package_test():
    _get_and_validate_files(
        _get_sphinx_from_artif_and_validate)


@with_setup(teardown=fixture.flush_caches)
def get_lowercase_sphinx_package_test():
    _get_and_validate_files(partial(
        _get_sphinx_from_artif_and_validate,
        lowercase_package=True))
