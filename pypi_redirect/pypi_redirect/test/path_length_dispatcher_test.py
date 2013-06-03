from nose.tools import eq_
from pypi_redirect.handler._exception import HandlerException
from pypi_redirect.http.path_length_dispatcher import PathLengthDispatcher
from pypi_redirect.test._utils import FunctionStub


def test_all_permutations():
    permutations = (
        TestHelper(0, False, False),
        TestHelper(0, True, False),
        TestHelper(0, False, True),

        TestHelper(1, False, False),
        TestHelper(1, True, False),
        TestHelper(1, False, True),

        TestHelper(2, False, False),
        TestHelper(2, True, False),
        TestHelper(2, False, True),
    )

    for permutation in permutations:
        yield permutation.perform_assertions


class _UniqueException(Exception):
    pass


class TestHelper(object):
    def __init__(
            self,
            number_of_handlers,
            normal_handlers_do_throw_exceptions,
            exception_handler_does_throw_exception):

        self.number_of_handlers = number_of_handlers

        self.normal_handlers_do_throw_exceptions \
            = normal_handlers_do_throw_exceptions
        self.exception_handler_does_throw_exception \
            = exception_handler_does_throw_exception

        self.normal_handlers = _create_normal_handlers(
            number_of_handlers,
            normal_handlers_do_throw_exceptions)

        self.exception_handler = _create_exception_handler(
            exception_handler_does_throw_exception)

        self.dispatcher = PathLengthDispatcher(
            handlers_indexed_by_path_length=self.normal_handlers,
            invalid_path_handler=self.exception_handler)

    def _assert_normal_handler_behavior(self):
        for n in xrange(self.number_of_handlers):
            try:
                path = ['item'] * n
                actual_result = self.dispatcher.default(*path)
                eq_(actual_result, self.normal_handlers[n].dummy_result)

            except _UniqueException:
                assert (
                    self.normal_handlers_do_throw_exceptions,
                    'Caught unexpected exception from normal handler')

    def _assert_exception_handler_behavior(self):
        try:
            path = ['item'] * self.number_of_handlers
            actual_result = self.dispatcher.default(*path)
            eq_(actual_result, self.exception_handler.dummy_result)

        except _UniqueException:
            assert (
                self.exception_handler_does_throw_exception,
                'Caught unexpected exception from invalid path handler')

    def perform_assertions(self):
        self._assert_normal_handler_behavior()
        self._assert_exception_handler_behavior()


def _create_normal_sad_handlers(number_of_handlers):
    handlers = []
    for n in xrange(number_of_handlers):
        handlers.append(FunctionStub(
            name='Path length {} handler'.format(n),
            dummy_exception=HandlerException(
                wrapped_exception=_UniqueException)))
    return handlers


def _create_normal_happy_handlers(number_of_handlers):
    handlers = []
    for n in xrange(number_of_handlers):
        handlers.append(FunctionStub(
            name='Path length {} handler'.format(n),
            dummy_result='Path length {} handler result'.format(n)))
    return handlers


def _create_sad_exception_handler():
    handler = FunctionStub(
        name='Invalid path handler',
        dummy_exception=_UniqueException)
    return handler


def _create_happy_exception_handler():
    handler = FunctionStub(
        name='Invalid path handler',
        dummy_result='Invalid path handler result')
    return handler


def _create_normal_handlers(
        number_of_handlers,
        normal_handlers_do_throw_exceptions):

    if normal_handlers_do_throw_exceptions:
        handlers = _create_normal_sad_handlers(number_of_handlers)
    else:
        handlers = _create_normal_happy_handlers(number_of_handlers)
    return handlers


def _create_exception_handler(
        exception_handler_does_throw_exception):

    if exception_handler_does_throw_exception:
        exception_handler = _create_sad_exception_handler()
    else:
        exception_handler = _create_happy_exception_handler()
    return exception_handler