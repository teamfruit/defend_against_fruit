from nose.tools import eq_
from _fixture import create_fixture
import _assertion_helper


fixture = create_fixture()


def setup_module():
    fixture.proxy.start()
    fixture.proxy.block_until_up()


def teardown_module():
    fixture.proxy.stop()


def proxy_root_trailing_slash_test():
    actual_result = fixture.proxy.parse_listing()
    expected_result = ('python/',)
    eq_(actual_result, expected_result)


def proxy_root_no_trailing_slash_test():
    _assert_redirect_for_proxy_path(
        from_path='python',
        to_path='python/',
        expected_code=301,
    )


def proxy_python_trailing_slash_test():
    actual_result = fixture.proxy.parse_listing(path='python/')
    assert '3to2/' in actual_result
    assert 'nose/' in actual_result
    assert 'Sphinx/' in actual_result


def proxy_python_no_trailing_slash_test():
    _assert_redirect_for_proxy_path(
        from_path='python',
        to_path='python/',
        expected_code=301,
    )


def proxy_nose_trailing_slash_test():
    actual_result = fixture.proxy.parse_listing(path='python/nose/')
    assert 'nose-1.2.1.tar.gz' in actual_result
    assert 'nose-1.3.0.tar.gz' in actual_result


def proxy_nose_no_trailing_slash_test():
    _assert_redirect_for_proxy_path(
        from_path='python/nose',
        to_path='python/nose/',
        expected_code=301,
    )


def proxy_get_sphinx_uppercase_test():
    _assert_package_retrieval_behavior(lowercase=False)


def proxy_get_sphinx_lowercase_test():
    _assert_package_retrieval_behavior(lowercase=True)


def _assert_redirect_for_proxy_path(from_path, to_path, expected_code):
    expected_location = fixture.proxy.get_path(path=to_path)
    actual_result = fixture.proxy.get_url(path=from_path)

    eq_(len(actual_result.history), 1)
    eq_(actual_result.history[0].status_code, expected_code)
    eq_(actual_result.history[0].headers['location'], expected_location)
    eq_(actual_result.status_code, 200)


def _assert_404_for_proxy_path(path):
    actual_result = fixture.proxy.get_url(path=path)
    eq_(actual_result.status_code, 404)


def _assert_package_retrieval_behavior(lowercase):
    helper = _assertion_helper.SphinxHelper(
        get_path_fn=fixture.proxy.get_url,
        lowercase=lowercase)

    # The package cached assertions are the only ones relevant to
    # the proxy. Since Artifactory is out of the picture, the cache
    # within Artifactory is irrelevant.
    _assertion_helper.perform_package_cached_assertions(
        sphinx_helper=helper,
        expect_artifactory_specific_headers=False)
