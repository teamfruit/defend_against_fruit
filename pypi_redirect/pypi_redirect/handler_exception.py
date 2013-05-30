import sys


class HandlerException(Exception):
    def __init__(self, wrapped_exception):
        self.wrapped_exception = wrapped_exception

    def raise_wrapped(self):
        """
        Raises the 'wrapped' exception, preserving the original backtrace.
        This must be called from within an `except` block.
        """
        # The first item is a class instance, so the second item must be None.
        # The third item is the traceback object, which is why this method must
        # be called from within an `except` block.
        raise (
            self.wrapped_exception(),
            None,
            sys.exc_info()[2])
