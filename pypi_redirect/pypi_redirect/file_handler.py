from functools import partial
import os
import cherrypy
from lxml.etree import ParseError
from requests import RequestException
from handler_exception import HandlerException


# TODO: add logging (in a test-friendly way)


class FileHandler(object):
    def __init__(self, pypi_base_url, http_get_fn, parse_index_fn):
        self.pypi_base_url = pypi_base_url
        self.http_get_fn = http_get_fn
        self.parse_index_fn = parse_index_fn

    def _is_checksum_file(self, filename):
        return filename.lower().endswith(('.md5', '.sha1'))

    def _handle_checksum(self, checksum_filename, index_rows, response):
        filename_base, ext = os.path.splitext(checksum_filename)
        ext_no_dot = ext[1:].lower()
        _ensure_file_in_index(filename=filename_base, index_rows=index_rows)
        checksums = index_rows[filename_base].checksums

        return _get_checksum(
            checksums=checksums,
            checksum_ext=ext_no_dot,
            response_headers=response.headers)

    def _redirect_to_download_url(self, filename, index_rows):
        _ensure_file_in_index(filename=filename, index_rows=index_rows)
        download_url = index_rows[filename].download_url
        raise _302(download_url)

    def handle(self, path, request, response):
        package_name, filename = path

        index_url = '{}/{}/'.format(self.pypi_base_url, package_name)

        index_rows = _fetch_and_parse_index(
            http_get_fn=self.http_get_fn,
            parse_index_fn=self.parse_index_fn,
            pypi_base_url=self.pypi_base_url,
            index_url=index_url,
            package_path=package_name)

        if self._is_checksum_file(filename=filename):
            return self._handle_checksum(
                checksum_filename=filename,
                index_rows=index_rows,
                response=response)

        self._redirect_to_download_url(
            filename=filename,
            index_rows=index_rows)


def _ensure_file_in_index(filename, index_rows):
    if filename not in index_rows:
        raise _404('File "{}" does not exist'.format(filename))


def _get_checksum(checksums, checksum_ext, response_headers):
    checksum = getattr(checksums, checksum_ext)

    if not checksum:
        raise _404('Checksum not available')

    response_headers['Content-Type'] = 'application/x-checksum'

    return checksum


def _404(message):
    return HandlerException(wrapped_exception=partial(
        cherrypy.HTTPError,
        status=404,
        message=message))


def _302(download_url):
    return HandlerException(wrapped_exception=partial(
        cherrypy.HTTPRedirect,
        urls=download_url,
        status=302))


def _fetch_and_parse_index(
        http_get_fn,
        parse_index_fn,
        pypi_base_url,
        index_url,
        package_path):
    try:
        index_html_str = http_get_fn(url=index_url)
    except RequestException:
        raise _404('Index "{}" cannot be reached'.format(index_url))

    try:
        index_rows = parse_index_fn(
            base_url=pypi_base_url,
            package_path=package_path,
            html_str=index_html_str)
    except ParseError:
        raise _404('Index "{}" failed to be parsed'.format(index_url))

    return index_rows
