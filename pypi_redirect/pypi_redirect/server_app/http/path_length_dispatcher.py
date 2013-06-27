import cherrypy
from ..handler._exception import HandlerException


class PathLengthDispatcher(object):
    def __init__(
            self,
            handlers_indexed_by_path_length,
            invalid_path_handler):
        self.handlers_indexed_by_path_length = handlers_indexed_by_path_length
        self.invalid_path_handler = invalid_path_handler

    @cherrypy.expose
    def default(self, *path):
        try:
            return self.handlers_indexed_by_path_length[len(path)](
                path=path,
                request=cherrypy.request,
                response=cherrypy.response)

        except IndexError:
            return self.invalid_path_handler(
                path=path,
                request=cherrypy.request,
                response=cherrypy.response)

        except HandlerException as e:
            e.raise_wrapped()
