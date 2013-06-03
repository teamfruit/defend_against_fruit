from collections import OrderedDict
from _utils import ensure_index


class RootIndexHandler(object):
    def __init__(self, build_index_fn):
        self.build_index_fn = build_index_fn

    @ensure_index
    def handle(self, path, request, response):
        html_str = self.build_index_fn(
            package_path='/',
            index_rows=OrderedDict([('python/', None)]))

        return html_str