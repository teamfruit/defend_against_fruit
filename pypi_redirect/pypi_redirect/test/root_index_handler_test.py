from collections import OrderedDict
from functools import partial
from nose.tools import eq_
from _test_utils import RequestStub, FunctionStub, ResponseStub
from _test_utils import assert_http_redirect


def empty_path_is_index_test():
    _check_root_path([], is_index=True)


def empty_path_not_index_test():
    handler_runner = partial(
        _check_root_path,
        path=[],
        is_index=False)

    assert_http_redirect(
        run_handler_fn=handler_runner,
        expected_url='/',
        expected_status=301,
        failure_description='Index handler did not redirect to directory')


def _check_root_path(path, is_index):
    dumb_response = "be dumb"

    builder_stub = FunctionStub(
        name='Builder',
        dummy_result=dumb_response)

    handler = RootIndexHandler(build_index_fn=builder_stub)
    request = RequestStub(is_index=is_index)
    response = ResponseStub()

    response_str = handler.handle(
        path=path,
        request=request,
        response=response)

    eq_(response.headers, {},
        msg='Headers are expected to be unaffected')

    eq_(response_str, dumb_response,
        msg='Handler did not return builder result')

    builder_stub.assert_single_kw_call(expected_kwargs={
        'package_path': '/',
        'index_rows': OrderedDict([('python/', None)])})
