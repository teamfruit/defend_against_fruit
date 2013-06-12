from _util import _return_when_web_service_up


class ProxyTestHelper(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def block_until_up(self, attempts=5):
        _return_when_web_service_up(
            health_check_url=self.base_url,
            attempts=attempts)
