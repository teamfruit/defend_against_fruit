from nose.plugins.attrib import attr
from nose.tools import eq_, with_setup
from _fixture import create_fixture
from _utils import assert_sphinx_packages
from _proxy_test_helper import proxy_brought_down
import _assertion_helper


fixture = create_fixture()


def setup_module():
    fixture.artif.block_until_up()
    fixture.proxy.start()
    fixture.proxy.block_until_up()

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


@attr('known_artif_bug')
def artif_pypi_root_nothing_cached_test():
    _assert_404_for_artif_path(path='python/')


@attr('known_artif_bug')
@with_setup(teardown=fixture.artif.flush_caches)
def artif_pypi_root_one_cached_test():
    fixture.artif.cache_packages(
        'python/Sphinx/Sphinx-1.1.3.tar.gz',
    )
    actual_result = fixture.artif.parse_listing(path='python/')

    eq_(len(actual_result), 2)
    assert '../' in actual_result
    assert 'Sphinx/' in actual_result


@attr('known_artif_bug')
@with_setup(teardown=fixture.artif.flush_caches)
def artif_pypi_root_three_cached_test():
    fixture.artif.cache_packages(
        'python/3to2/3to2-1.0.tar.gz',
        'python/nose/nose-1.3.0.tar.gz',
        'python/Sphinx/Sphinx-1.1.3.tar.gz',
    )
    actual_result = fixture.artif.parse_listing(path='python/')

    eq_(len(actual_result), 4)
    assert '../' in actual_result
    assert '3to2/' in actual_result
    assert 'nose/' in actual_result
    assert 'Sphinx/' in actual_result


def artif_uppercase_sphinx_no_slash_test():
    _assert_404_for_artif_path(path='python/Sphinx')


def artif_lowercase_sphinx_no_slash_test():
    _assert_404_for_artif_path(path='python/sphinx')


def artif_uppercase_sphinx_test():
    actual_result = fixture.artif.parse_listing(path='python/Sphinx/')
    assert_sphinx_packages(actual_result)


def artif_lowercase_sphinx_test():
    actual_result = fixture.artif.parse_listing(path='python/sphinx/')
    assert_sphinx_packages(actual_result)


def artif_invalid_package_test():
    _assert_404_for_artif_path(path='python/NotARealPackage/')


def artif_invalid_file_test():
    _assert_404_for_artif_path(path='python/Sphinx/NotARealFile.tar.gz')


@with_setup(teardown=fixture.artif.flush_caches)
def get_uppercase_sphinx_package_test():
    _assert_package_retrieval_behavior(lowercase=False)


@with_setup(teardown=fixture.artif.flush_caches)
def get_lowercase_sphinx_package_test():
    _assert_package_retrieval_behavior(lowercase=True)


def _assert_404_for_artif_path(path):
    actual_result = fixture.artif.get_repo_url(path=path)
    eq_(actual_result.status_code, 404)


def _assert_package_retrieval_behavior(lowercase):
    helper = _assertion_helper.SphinxHelper(
        get_path_fn=fixture.artif.get_repo_url,
        lowercase=lowercase)

    _assertion_helper.perform_package_not_cached_assertions(helper)
    _assertion_helper.perform_package_cached_assertions(
        sphinx_helper=helper,
        expect_artifactory_specific_headers=True)

    with proxy_brought_down(fixture.proxy):
        _assertion_helper.perform_package_cached_assertions(
            sphinx_helper=helper,
            expect_artifactory_specific_headers=True)

        fixture.artif.flush_caches()
        _assertion_helper.perform_package_unavailable_assertions(helper)
