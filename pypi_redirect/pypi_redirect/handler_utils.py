from lxml.etree import ParseError
from requests import RequestException
from pypi_redirect.handler_exception import http_404, http_301


def ensure_index(fn):
    """
    Decorator for the handle() method of any handler. Ensures that
    indexes requested without a trailing slash are redirected to a
    version with the trailing slash.
    """
    def wrapper(self, path, request, response):
        if not request.is_index:
            raise http_301('/'.join(path) + '/')
        return fn(self, path, request, response)
    return wrapper


def fetch_and_parse_index(
        http_get_fn,
        parse_index_fn,
        pypi_base_url,
        index_url,
        package_path):
    try:
        index_html_str = http_get_fn(url=index_url)
    except RequestException:
        raise http_404('Index "{}" cannot be reached'.format(index_url))

    try:
        index_rows = parse_index_fn(
            base_url=pypi_base_url,
            package_path=package_path,
            html_str=index_html_str)
    except ParseError:
        raise http_404('Index "{}" failed to be parsed'.format(index_url))

    return index_rows
