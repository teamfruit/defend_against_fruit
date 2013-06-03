from _utils import fetch_and_parse_index, ensure_index, ensure_python_dir


# TODO: add logging (in a test-friendly way)
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

    @ensure_python_dir
    @ensure_index
    def handle(self, path, request, response):
        if len(path) == 2:
            py, package_name = path
            index_url = '{}/{}/'.format(self.pypi_base_url, package_name)
        else:
            package_name = ''
            index_url = '{}/'.format(self.pypi_base_url)

        index_rows = fetch_and_parse_index(
            http_get_fn=self.http_get_fn,
            parse_index_fn=self.parse_index_fn,
            pypi_base_url=self.pypi_base_url,
            index_url=index_url,
            package_path=package_name)

        rebuilt_html_str = self.build_index_fn(
            package_path=package_name,
            index_rows=index_rows)

        return rebuilt_html_str