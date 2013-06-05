import index_builder
import index_parser
from handler.file_handler import FileHandler
from handler.invalid_path_handler import InvalidPathHandler
from handler.pypi_index_handler import PyPIIndexHandler
from handler.root_index_handler import RootIndexHandler
from http._utils import http_get
from http.path_length_dispatcher import PathLengthDispatcher


def wire_dependencies():
    """
    PyPI redirect uses a dependency injection paradigm to better
    facilitate testing. Rather than use a dependency injection
    framework, we are manually injecting our dependencies here.
    """
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

    root = PathLengthDispatcher(
        handlers_indexed_by_path_length=(
            root_index_handler.handle,  # len 0: ex: /
            pypi_index_handler.handle,  # len 1: ex: /python/
            pypi_index_handler.handle,  # len 2: ex: /python/nose/
            file_handler.handle),       # len 3: ex: /python/nose/nose-1.0.tgz
        invalid_path_handler=invalid_path_handler)

    return root