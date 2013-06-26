from _exception import http_404


class InvalidPathHandler(object):
    def handle(self, path, request, response):
        raise http_404('Invalid path of "{}"'.format('/'.join(path)))
