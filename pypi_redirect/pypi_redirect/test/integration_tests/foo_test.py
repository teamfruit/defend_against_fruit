def setup_module():
    print 'FixtureFoo.setup'


def teardown_module():
    print 'FixtureFoo.teardown'


def foo1_test():
    print '    foo1_test'


def foo2_test():
    print '    foo2_test'


def foo3_test():
    print '    foo3_test'









# from time import sleep
# import requests
#
#
# # Proxy Test Categories
# # - One URL redirects to another with given code
# # - URL creates 404
# # - URL generates listing (NOTE: Inspect HTML results)
#
#
# def foo_test():
#     artifactory_test_helper = ArtifactoryTestHelper(
#         base_url='http://localhost:8081/artifactory',
#         pypi_repo_id='pypi-remote')
#
#     proxy_test_helper = ProxyTestHelper(
#         base_url='http://localhost:9292')
#
#     _assert_services_up(services=(
#         artifactory_test_helper,
#         proxy_test_helper))
#
#     # print requests.get(
#     #     'http://localhost:8081/artifactory/pypi-remote/').text
#
#
# def _assert_services_up(services):
#     for s in services:
#         s.block_until_up()
#
#
# class ArtifactoryTestHelper(object):
#     def __init__(self, base_url, pypi_repo_id):
#         self.base_url = base_url
#         self.pypi_repo_id = pypi_repo_id
#
#     def clean_pypi_repo(self):
#         url = '/'.join((self.base_url, self.pypi_repo_id, 'python'))
#         result = requests.delete(url)
#         result.raise_for_status()
#
#     def block_until_up(self, attempts=5):
#         url = '/'.join((self.base_url, 'api/system/ping'))
#         _return_when_web_service_up(
#             health_check_url=url,
#             attempts=attempts)
#
#
# class ProxyTestHelper(object):
#     def __init__(self, base_url):
#         self.base_url = base_url
#
#     def block_until_up(self, attempts=5):
#         _return_when_web_service_up(
#             health_check_url=self.base_url,
#             attempts=attempts)
#
#
# def _return_when_web_service_up(health_check_url, attempts=5):
#     while True:
#         try:
#             response = requests.get(health_check_url, timeout=1)
#             response.raise_for_status()
#         except requests.RequestException:
#             pass
#         else:
#             break
#
#         if attempts <= 0:
#             raise AssertionError(
#                 'Failed to connect to {}'.format(health_check_url))
#
#         attempts -= 1
#         sleep(1)