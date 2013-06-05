from collections import OrderedDict, namedtuple
from functools import partial
from lxml.etree import ParseError
from nose.tools import eq_
from requests import RequestException
from pypi_redirect.server_app.handler.file_handler import FileHandler
from pypi_redirect.server_app.index_parser import IndexRow, Checksums
from _utils import FunctionStub, RequestStub, ResponseStub
from _utils import assert_http_redirect, assert_http_not_found


FileEntry = namedtuple('FileEntry', ('pkg_name', 'filename', 'index_row'))


def _generate_file_entry(has_md5=True, has_sha1=True):
    checksums = Checksums(
        md5='MD5-nose-1.2.1.tar.gz' if has_md5 else None,
        sha1='SHA1-nose-1.2.1.tar.gz' if has_sha1 else None)

    file_entry = FileEntry(
        pkg_name='nose',
        filename='nose-1.2.1.tar.gz',
        index_row=IndexRow(
            download_url='http://some_url.com/nose/nose-1.2.1.tar.gz',
            checksums=checksums))

    return file_entry


def handle_file_request_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename)

    assert_http_redirect(
        run_handler_fn=handler_runner,
        expected_url=file_entry.index_row.download_url,
        expected_status=302,
        failure_description='Handler did not redirect')


def handle_md5_request_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename + '.md5',
        expected_checksum=file_entry.index_row.checksums.md5)

    handler_runner()


def handle_sha1_request_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename + '.sha1',
        expected_checksum=file_entry.index_row.checksums.sha1)

    handler_runner()


def handle_non_existent_file_request_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested='non-existent.tar.gz')

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 for non-existent file')


def handle_non_existent_md5_request_test():
    file_entry = _generate_file_entry(has_md5=False)

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename + '.md5')

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 for non-existent file')


def handle_non_existent_sha1_request_test():
    file_entry = _generate_file_entry(has_sha1=False)

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename + '.sha1')

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 for non-existent file')


def http_get_fn_exception_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename,
        http_get_exception=RequestException())

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on failure to get index')


def parse_index_fn_exception_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename,
        parse_index_exception=ParseError(None, None, None, None))

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on failure to parse index')


def non_python_root_path_test():
    file_entry = _generate_file_entry()

    handler_runner = partial(
        _check_file_handler,
        file_entry=file_entry,
        file_requested=file_entry.filename,
        root_dir='not_python')

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on non-"/python/" path')


def _check_file_handler(
        file_entry,
        file_requested,
        root_dir='python',
        expected_checksum=None,
        http_get_exception=None,
        parse_index_exception=None):

    pypi_base_url = 'http://dumb_url.com'

    parser_response = OrderedDict([
        ('nose-1.2.0.tar.gz', IndexRow(
            download_url='http://some_url.com/nose/nose-1.2.0.tar.gz',
            checksums=Checksums(
                md5='MD5-nose-1.2.0.tar.gz',
                sha1=None))),
        (file_entry.filename, file_entry.index_row),
        ('nose-1.2.1.egg', IndexRow(
            download_url='http://some_url.com/nose/nose-1.2.1.egg',
            checksums=Checksums(
                md5='MD5-nose-1.2.1.egg',
                sha1=None))),
    ])

    html_get_response = 'be dumb html'

    html_get_stub = FunctionStub(
        name='HTML Get',
        dummy_result=html_get_response,
        dummy_exception=http_get_exception)

    parser_stub = FunctionStub(
        name='Parser',
        dummy_result=parser_response,
        dummy_exception=parse_index_exception)

    handler = FileHandler(
        pypi_base_url=pypi_base_url,
        http_get_fn=html_get_stub,
        parse_index_fn=parser_stub)

    request = RequestStub(is_index=False)
    response = ResponseStub()

    # When not retrieving a checksum, we expect a redirection exception to be
    # thrown here. Asserting correct redirect behavior is performed in the
    # calling test function.
    response_str = handler.handle(
        path=[root_dir, file_entry.pkg_name, file_requested],
        request=request,
        response=response)

    expected_headers = {'Content-Type': 'application/x-checksum'}

    eq_(response.headers, expected_headers,
        msg='Response headers did not match the expected headers')

    eq_(response_str, expected_checksum,
        msg='Response checksum did not match the expected checksum')

    html_get_stub.assert_single_kw_call(expected_kwargs={
        'url': '{}/{}/'.format(pypi_base_url, file_entry.pkg_name)})

    parser_stub.assert_single_kw_call(expected_kwargs={
        'base_url': pypi_base_url,
        'package_path': file_entry.pkg_name,
        'html_str': html_get_response})
