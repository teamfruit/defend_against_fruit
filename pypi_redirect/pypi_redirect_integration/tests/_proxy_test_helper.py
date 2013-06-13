import subprocess
import sys
from _utils import return_when_web_service_up


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
