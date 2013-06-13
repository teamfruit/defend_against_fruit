from functools import partial
from nose.tools import eq_, with_setup
from _fixture import create_fixture
from _utils import get_sphinx_from_url_and_validate, assert_sphinx_packages
from _utils import assert_services_up


fixture = create_fixture()


def setup_module():
    fixture.proxy.start()

    assert_services_up(services=(
        fixture.artif,
        fixture.proxy))

    # These tests assume nothing is cached in Artifactory.
    fixture.artif.flush_caches()


def teardown_module():
    fixture.proxy.stop()


def artif_root_test():
    actual_result = fixture.artif.parse_listing()
    expected_result = ('python/',)
    eq_(actual_result, expected_result)


def artif_pypi_root_no_slash_test():
    _assert_404_for_artif_path(path='python')


def artif_pypi_root_test():
    _assert_404_for_artif_path(path='python/')


def artif_sphinx_no_slash_test():
    _assert_404_for_artif_path(path='python/Sphinx')


def artif_lowercase_sphinx_no_slash_test():
    _assert_404_for_artif_path(path='python/sphinx')


def artif_sphinx_test():
    actual_result = fixture.artif.parse_listing(path='python/Sphinx/')
    assert_sphinx_packages(actual_result)


def artif_lowercase_sphinx_test():
    actual_result = fixture.artif.parse_listing(path='python/sphinx/')
    assert_sphinx_packages(actual_result)


@with_setup(teardown=fixture.artif.flush_caches)
def get_sphinx_package_test():
    _get_and_validate_files(partial(
        get_sphinx_from_url_and_validate,
        get_url_fn=fixture.artif.get_repo_url))


@with_setup(teardown=fixture.artif.flush_caches)
def get_lowercase_sphinx_package_test():
    _get_and_validate_files(partial(
        get_sphinx_from_url_and_validate,
        get_url_fn=fixture.artif.get_repo_url,
        lowercase_package=True))


def _assert_404_for_artif_path(path):
    actual_result = fixture.artif.get_repo_url(path=path)
    eq_(actual_result.status_code, 404)


def _get_and_validate_files(get_and_validate_fn):
    ### 1. Package not cached.

    # a. Verify that getting the MD5 fails before the package is requested.
    get_and_validate_fn(checksum_ext='.md5', expect_md5_not_found=True)

    # b. Verify that getting the SHA1 fails before the package is requested.
    get_and_validate_fn(checksum_ext='.sha1')

    # c. Request package to cache it.
    get_and_validate_fn()

    ### 2. Package cached.

    # a. Verify that getting the MD5 succeeds after the package is cached.
    get_and_validate_fn(checksum_ext='.md5')

    # b. Verify that getting the SHA1 *still* fails after the package is
    #    cached (the proxy is not returning an SHA1 checksum).
    get_and_validate_fn(checksum_ext='.sha1')

    # c. Get the cached package again and verify that it still looks the same.
    get_and_validate_fn()
