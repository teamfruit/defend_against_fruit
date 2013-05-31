from collections import OrderedDict
from handler_exception import http_301


# TODO: add logging (in a test-friendly way)
class RootIndexHandler(object):
    def __init__(self, build_index_fn):
        self.build_index_fn = build_index_fn

    def handle(self, path, request, response):
        if not request.is_index:
            raise http_301('/'.join(path) + '/')

        html_str = self.build_index_fn(
            package_path='/',
            index_rows=OrderedDict([('python/', None)]))

        return html_str