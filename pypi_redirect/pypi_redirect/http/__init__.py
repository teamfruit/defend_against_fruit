from pypi_redirect import index_builder, index_parser
from pypi_redirect.handler.file_handler import FileHandler
from pypi_redirect.handler.invalid_path_handler import InvalidPathHandler
from pypi_redirect.handler.pypi_index_handler import PyPIIndexHandler
from pypi_redirect.handler.root_index_handler import RootIndexHandler
from _utils import http_get
from root import Root


def wire():
    pypi_base_url = 'https://pypi.python.org/simple'

    root_index_handler = RootIndexHandler(
        build_index_fn=index_builder.build)

    pypi_index_handler = PyPIIndexHandler(
        pypi_base_url=pypi_base_url,
        http_get_fn=http_get,
        parse_index_fn=index_parser.parse,
        build_index_fn=index_builder.build)

    file_handler = FileHandler(
        pypi_base_url=pypi_base_url,
        http_get_fn=http_get,
        parse_index_fn=index_parser.parse)

    invalid_path_handler = InvalidPathHandler()

    root = Root(
        handlers=(
            root_index_handler,
            pypi_index_handler,
            pypi_index_handler,
            file_handler),
        invalid_path_handler=invalid_path_handler)

    return root
