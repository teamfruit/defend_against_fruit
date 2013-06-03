from nose.tools import eq_
from pypi_redirect.handler._exception import HandlerException
from pypi_redirect.http.path_length_dispatcher import PathLengthDispatcher
from pypi_redirect.test._utils import FunctionStub


def test_all_permutations():
    permutations = (
        (0, False, False),
        (0, True, False),
        (0, False, True),
        (1, False, False),
        (1, True, False),
        (1, False, True),
        (2, False, False),
        (2, True, False),
        (2, False, True),
    )

    for (
        number_of_handlers,
        normal_handlers_do_throw_exceptions,
        exception_handler_does_throw_exception
    ) in permutations:
        yield (
            _assert_single_permutation,
            number_of_handlers,
            normal_handlers_do_throw_exceptions,
            exception_handler_does_throw_exception)


class _UniqueException(Exception):
    pass


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


def _assert_single_permutation(
        number_of_handlers,
        normal_handlers_do_throw_exceptions,
        exception_handler_does_throw_exception):

    #
    if normal_handlers_do_throw_exceptions:
        normal_handlers = _create_normal_sad_handlers(number_of_handlers)
    else:
        normal_handlers = _create_normal_happy_handlers(number_of_handlers)

    #
    if exception_handler_does_throw_exception:
        exception_handler = _create_sad_exception_handler()
    else:
        exception_handler = _create_happy_exception_handler()

    dispatcher = PathLengthDispatcher(
        handlers_indexed_by_path_length=normal_handlers,
        invalid_path_handler=exception_handler)

    for n in xrange(number_of_handlers):
        try:
            path = ['item'] * n
            actual_result = dispatcher.default(*path)
            eq_(actual_result, normal_handlers[n].dummy_result)

        except _UniqueException:
            assert (
                normal_handlers_do_throw_exceptions,
                'Caught unexpected exception from normal handler')

    try:
        path = ['item'] * number_of_handlers
        actual_result = dispatcher.default(*path)
        eq_(actual_result, exception_handler.dummy_result)

    except _UniqueException:
        assert (
            exception_handler_does_throw_exception,
            'Caught unexpected exception from invalid path handler')
