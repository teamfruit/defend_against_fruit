import os
from nose.tools import eq_
from ..server_app.handler._exception import HandlerException


def read_index(filename):
    index_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'resources', filename)

    with open(index_path) as f:
        return f.read()


class FunctionStub(object):
    def __init__(self, name, dummy_result=None, dummy_exception=None):
        self.name = name
        self.dummy_result = dummy_result
        self.dummy_exception = dummy_exception
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))

        if self.dummy_exception is not None:
            raise self.dummy_exception

        return self.dummy_result

    def assert_single_kw_call(self, expected_kwargs):
        eq_(len(self.calls), 1,
            msg='{} was called more than once'.format(self.name))

        eq_(len(self.calls[0][0]), 0,
            msg='{} was called with non-named arguments'.format(self.name))

        eq_(self.calls[0][1], expected_kwargs,
            msg='{} was not called with expected arguments'.format(self.name))


class RequestStub(object):
    def __init__(self, is_index):
        self.is_index = is_index


class ResponseStub(object):
    def __init__(self):
        self.headers = {}


def assert_http_not_found(run_handler_fn, failure_description):
    try:
        run_handler_fn()

    except HandlerException as e:
        kwargs = e.wrapped_exception.keywords

        assert 'status' in kwargs, \
            'No http status specified ' \
            '(expected `status` keyword)'

        eq_(kwargs['status'], 404,
            msg='Expected 404 http status')

    except:
        raise AssertionError('Failed to raise a HandlerException')

    else:
        raise AssertionError(failure_description)


def assert_http_redirect(
        run_handler_fn,
        expected_url,
        expected_status,
        failure_description):
    try:
        run_handler_fn()

    except HandlerException as e:
        kwargs = e.wrapped_exception.keywords

        assert 'urls' in kwargs, \
            'No URL specified for redirection ' \
            '(expected `urls` keyword argument)'

        assert 'status' in kwargs, \
            'No redirect status specified ' \
            '(expected `status` keyword argument)'

        eq_(kwargs['urls'], expected_url,
            msg='Incorrect redirection URL')

        eq_(kwargs['status'], expected_status,
            msg='Incorrect redirection status')

    except:
        raise AssertionError('Failed to raise a HandlerException')

    else:
        raise AssertionError(failure_description)
