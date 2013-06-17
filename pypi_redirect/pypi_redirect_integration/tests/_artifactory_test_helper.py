import requests
from pypi_redirect.server_app import index_parser
from _utils import return_when_web_service_up, find_all_links


class ArtifactoryTestHelper(object):
    def __init__(self, base_url, pypi_repo_id, clean_credentials):
        self.base_url = base_url
        self.pypi_repo_id = pypi_repo_id
        self.pypi_cache_repo_id = pypi_repo_id + '-cache'
        self.clean_credentials = clean_credentials

    def __get_path(self, path):
        url = '/'.join((self.base_url, self.pypi_repo_id, path.lstrip('/')))
        return url

    def block_until_up(self, attempts=5):
        url = '/'.join((self.base_url, 'api/system/ping'))
        return_when_web_service_up(
            health_check_url=url,
            attempts=attempts)

    def flush_caches(self):
        url = '/'.join((self.base_url, self.pypi_cache_repo_id, 'python'))
        result = requests.delete(url, auth=self.clean_credentials)

        # 404 is returned when there are no artifacts to remove - this is okay.
        if result.status_code != 404:
            # Otherwise, check the return status for an error.
            result.raise_for_status()

    def get_repo_url(self, path='', only_headers=False):
        url = self.__get_path(path)
        result = requests.head(url) if only_headers else requests.get(url)
        return result

    def parse_listing(self, path=''):
        url = self.__get_path(path)
        result = requests.get(url)
        result.raise_for_status()

        html_str = result.text

        # Our index_parser.parse is very well unit-tested.
        rows = index_parser.parse(
            base_url=url,
            package_path='',
            html_str=html_str,
            strict_html=False,
            find_links_fn=find_all_links)

        return tuple(rows.iterkeys())

    def cache_packages(self, *paths):
        for p in paths:
            r = self.get_repo_url(path=p)
            r.raise_for_status()