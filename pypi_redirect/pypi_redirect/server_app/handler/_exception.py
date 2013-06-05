from functools import partial
import sys
import cherrypy


class HandlerException(Exception):
    def __init__(self, wrapped_exception):
        self.wrapped_exception = wrapped_exception

    def raise_wrapped(self):
        """
        Raises the 'wrapped' exception, preserving the original
        traceback. This must be called from within an `except` block.
        """
        # The first item is a class instance, so the second item must
        # be None. The third item is the traceback object, which is why
        # this method must be called from within an `except` block.
        raise (
            self.wrapped_exception(),
            None,
            sys.exc_info()[2])


def http_301(download_url):
    return HandlerException(wrapped_exception=partial(
        cherrypy.HTTPRedirect,
        urls=download_url,
        status=301))


def http_302(download_url):
    return HandlerException(wrapped_exception=partial(
        cherrypy.HTTPRedirect,
        urls=download_url,
        status=302))


def http_404(message):
    return HandlerException(wrapped_exception=partial(
        cherrypy.HTTPError,
        status=404,
        message=message))