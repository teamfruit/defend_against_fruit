from lxml.etree import XMLSyntaxError
from nose.tools import eq_
from requests import RequestException
from _test_utils import RequestStub, ResponseStub, FunctionStub
from pypi_redirect.handler_exception import HandlerException


def typical_usage_as_index_test():
    _check_main_index_path(
        path=['python', 'nose'],
        is_index=True)


def typical_usage_not_index_test():
    try:
        _check_main_index_path(
            path=['python', 'nose'],
            is_index=False)

    except HandlerException as e:
        kwargs = e.wrapped_exception.keywords

        assert 'urls' in kwargs, 'No URL specified for redirection'
        assert 'status' in kwargs, 'No redirect status specified'

        eq_(kwargs['urls'], 'python/nose/',
            msg='Expected redirection to python/nose/')

        eq_(kwargs['status'], 301,
            msg='Expected 301 http redirect')
    else:
        raise AssertionError('Index handler did not redirect to directory')


def http_get_fn_exception_test():
    try:
        _check_main_index_path(
            path=['python', 'nose'],
            is_index=True,
            http_get_exception=RequestException())

    except HandlerException as e:
        kwargs = e.wrapped_exception.keywords

        assert 'status' in kwargs, 'No http status specified'

        eq_(kwargs['status'], 404,
            msg='Expected 404 http error')
    else:
        raise AssertionError('Failed to return 404 on failure to get index')


def parse_index_fn_exception_test():
    try:
        _check_main_index_path(
            path=['python', 'nose'],
            is_index=True,
            parse_index_exception=XMLSyntaxError())

    except HandlerException as e:
        kwargs = e.wrapped_exception.keywords

        assert 'status' in kwargs, 'No http status specified'

        eq_(kwargs['status'], 404,
            msg='Expected 404 http error')
    else:
        raise AssertionError('Failed to return 404 on failure to parse index')


def _check_main_index_path(
        path,
        is_index,
        http_get_exception=None,
        parse_index_exception=None):

    pypi_base_url = 'http://dumb_url.com'
    package_path = 'something'
    builder_response = 'be dumb builder'
    parser_response = 'be dumb parser'
    html_get_response = 'be dumb html'

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
        'package_path': package_path,
        'index_rows': parser_response})

    parser_stub.assert_single_kw_call(expected_kwargs={
        'base_url': pypi_base_url,
        'package_path': package_path,
        'html_str': html_get_response})


#############################
#Interface design notes
#########
#
# IHandler
#
#     handle(path, response) -> str
#
#
#
# root_index_handler : IHandler
#
#     ctr(build_index_fn)
#
#
# main_index_handler : IHandler
#
#     ctr(pypi_base_url, http_get_fn, parse_index_fn, build_index_fn)
#
#
# module_index_handler : IHandler
#
#     ctr(pypi_base_url, http_get_fn, parse_index_fn, build_index_fn)
#
#
# file_handler : IHandler
#
#     ctr(pypi_base_url, http_get_fn, parse_index_fn)
#
#
# invalid_path_handler : IHandler
#
#     ctr()
#
# ------------------------------------------------------------------------------
#
# PathLengthDispatcher
#
#     ctr(path_handlers, invalid_path_handler, find_response_fn)
#
#     default(*path) -> str
#         response = find_response_fn()
#         try:
#             return path_handlers[len(path)](path, response)
#         except IndexError:
#             return invalid_path_handler(path, response)