from functools import partial
from _artifactory_test_helper import ArtifactoryTestHelper
from _proxy_test_helper import ProxyTestHelper


class Fixture(object):
    def __init__(
            self,
            artif_base_url,
            pypi_repo_id,
            proxy_base_url,
            clean_cache_auth):

        self.artif = ArtifactoryTestHelper(
            base_url=artif_base_url.strip('/'),
            pypi_repo_id=pypi_repo_id.strip('/'),
            clean_credentials=clean_cache_auth)

        self.proxy = ProxyTestHelper(
            base_url=proxy_base_url.strip('/'))


create_fixture = partial(
    Fixture,
    artif_base_url='http://localhost:8081/artifactory',
    pypi_repo_id='pypi-remote',
    proxy_base_url='http://localhost:9292',
    clean_cache_auth=('admin', 'password'))
