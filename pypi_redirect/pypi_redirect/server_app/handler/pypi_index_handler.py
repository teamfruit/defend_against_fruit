from _utils import fetch_and_parse_index, ensure_index, ensure_python_dir


class PyPIIndexHandler(object):
    def __init__(
            self,
            pypi_base_url,
            http_get_fn,
            parse_index_fn,
            build_index_fn):
        self.pypi_base_url = pypi_base_url
        self.http_get_fn = http_get_fn
        self.parse_index_fn = parse_index_fn
        self.build_index_fn = build_index_fn

    def _simple_pypi_or_package(self, path):
        """
        Determines whether the given path points to a specific package
        or to the root of the "simple" PyPI structure.
        """
        if len(path) == 2:
            py, package_name = path
            index_url = '{}/{}/'.format(self.pypi_base_url, package_name)
        else:
            package_name = 'python'
            index_url = '{}/'.format(self.pypi_base_url)
        return index_url, package_name

    @ensure_python_dir
    @ensure_index
    def handle(self, path, request, response):
        index_url, package_name = self._simple_pypi_or_package(path)

        index_rows = fetch_and_parse_index(
            http_get_fn=self.http_get_fn,
            parse_index_fn=self.parse_index_fn,
            pypi_base_url=self.pypi_base_url,
            index_url=index_url,
            package_path=package_name)

        rebuilt_html_str = self.build_index_fn(
            index_rows=index_rows)

        return rebuilt_html_str