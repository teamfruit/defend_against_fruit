import requests
from _util import _return_when_web_service_up


class ArtifactoryTestHelper(object):
    def __init__(self, base_url, pypi_repo_id, clean_credentials):
        self.base_url = base_url
        self.pypi_repo_id = pypi_repo_id
        self.pypi_cache_repo_id = pypi_repo_id + '-cache'
        self.clean_credentials = clean_credentials

    def clean_pypi_repo(self):
        url = '/'.join((self.base_url, self.pypi_cache_repo_id, 'python'))
        result = requests.delete(url, auth=self.clean_credentials)

        # 404 is returned when there are no artifacts to remove - this is okay.
        if result.status_code != 404:
            # Otherwise, check the return status for an error.
            result.raise_for_status()

    def block_until_up(self, attempts=5):
        url = '/'.join((self.base_url, 'api/system/ping'))
        _return_when_web_service_up(
            health_check_url=url,
            attempts=attempts)
