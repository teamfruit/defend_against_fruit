from lxml.etree import ParseError
from requests import RequestException
from pypi_redirect.handler_exception import http_404


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
