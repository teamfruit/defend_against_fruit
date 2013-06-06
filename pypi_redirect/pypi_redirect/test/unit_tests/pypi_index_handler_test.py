from functools import partial
from lxml.etree import ParseError
from nose.tools import eq_
from requests import RequestException
from _utils import RequestStub, ResponseStub, FunctionStub
from _utils import assert_http_redirect, assert_http_not_found
from ...server_app.handler.pypi_index_handler import PyPIIndexHandler


def typical_usage_as_index_test():
    _check_main_index_path(
        path=['python', 'nose'],
        is_index=True)


def typical_usage_not_index_test():
    handler_runner = partial(
        _check_main_index_path,
        path=['python', 'nose'],
        is_index=False)

    assert_http_redirect(
        run_handler_fn=handler_runner,
        expected_url='nose/',
        expected_status=301,
        failure_description='Index handler did not redirect to directory')


def http_get_fn_exception_test():
    handler_runner = partial(
        _check_main_index_path,
        path=['python', 'nose'],
        is_index=True,
        http_get_exception=RequestException())

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on failure to get index')


def parse_index_fn_exception_test():
    handler_runner = partial(
        _check_main_index_path,
        path=['python', 'nose'],
        is_index=True,
        parse_index_exception=ParseError(None, None, None, None))

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on failure to parse index')


def non_python_root_path_test():
    handler_runner = partial(
        _check_main_index_path,
        path=['not_python', 'nose'],
        is_index=True)

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to return 404 on non-"/python/" path')


def _check_main_index_path(
        path,
        is_index,
        http_get_exception=None,
        parse_index_exception=None):

    pypi_base_url = 'http://dumb_url.com'
    builder_response = 'be dumb builder'
    parser_response = 'be dumb parser'
    html_get_response = 'be dumb html'
    py, package_path = path

    html_get_stub = FunctionStub(
        name='HTML Get',
        dummy_result=html_get_response,
        dummy_exception=http_get_exception)

    parser_stub = FunctionStub(
        name='Parser',
        dummy_result=parser_response,
        dummy_exception=parse_index_exception)

    builder_stub = FunctionStub(
        name='Builder',
        dummy_result=builder_response)

    handler = PyPIIndexHandler(
        pypi_base_url=pypi_base_url,
        http_get_fn=html_get_stub,
        parse_index_fn=parser_stub,
        build_index_fn=builder_stub)

    request = RequestStub(is_index=is_index)
    response = ResponseStub()

    response_str = handler.handle(
        path=path,
        request=request,
        response=response)

    eq_(response.headers, {},
        msg='Headers are expected to be unaffected')

    eq_(response_str, builder_response,
        msg='Handler did not return builder result')

    builder_stub.assert_single_kw_call(expected_kwargs={
        'index_rows': parser_response})

    parser_stub.assert_single_kw_call(expected_kwargs={
        'base_url': pypi_base_url,
        'package_path': package_path,
        'html_str': html_get_response})
