import subprocess
import sys
import requests
from _utils import return_when_web_service_up, return_when_web_service_down


class ProxyTestHelper(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def start(self):
        self.process = subprocess.Popen(
            [sys.executable, '-m', 'pypi_redirect'])

    def stop(self):
        self.process.terminate()

    def block_until_up(self, attempts=5):
        return_when_web_service_up(
            health_check_url=self.base_url,
            attempts=attempts)

    def block_until_down(self, attempts=5):
        return_when_web_service_down(
            health_check_url=self.base_url,
            attempts=attempts)

    def __get_path(self, path):
        url = '/'.join((self.base_url, path.lstrip('/')))
        return url

    def get_repo_url(self, path='', only_headers=False):
        url = self.__get_path(path)
        result = requests.head(url) if only_headers else requests.get(url)
        return result


def proxy_brought_down(proxy):
    class Context(object):
        def __enter__(self):
            proxy.stop()
            proxy.block_until_down()

        def __exit__(self, exc_type, exc_val, exc_tb):
            proxy.start()
            proxy.block_until_up()

    return Context()