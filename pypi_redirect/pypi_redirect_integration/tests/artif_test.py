from functools import partial
from nose.plugins.attrib import attr
from nose.tools import eq_, with_setup
from _fixture import create_fixture
from _utils import assert_sphinx_packages
from _proxy_test_helper import proxy_brought_down


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


def artif_invalid_package_test():
    _assert_404_for_artif_path(path='python/NotARealPackage/')


def artif_invalid_file_test():
    _assert_404_for_artif_path(path='python/Sphinx/NotARealFile.tar.gz')


@with_setup(teardown=fixture.artif.flush_caches)
def get_sphinx_package_test():
    _assert_package_retrieval_behavior(lowercase=False)


@with_setup(teardown=fixture.artif.flush_caches)
def get_lowercase_sphinx_package_test():
    _assert_package_retrieval_behavior(lowercase=True)


def _assert_404_for_artif_path(path):
    actual_result = fixture.artif.get_repo_url(path=path)
    eq_(actual_result.status_code, 404)


def _validate_content_type(expected_type, result):
    eq_(result.headers['Content-Type'], expected_type)


def _validate_content_length(expected_length, result):
    eq_(int(result.headers['content-length']), expected_length)


def _validate_md5(expected_md5, result):
    eq_(result.headers['x-checksum-md5'], expected_md5)


def _validate_text(expected_text, result):
    eq_(result.text, expected_text)


def _validate_404(result):
    eq_(result.status_code, 404)


def _get_path_and_perform_validations(path, validate_fn_list):
    result = fixture.artif.get_repo_url(path)

    for v in validate_fn_list:
        v(result)


class SphinxHelper(object):
    def __init__(self, lowercase=False):
        self._package_prefix = 'python/{}/'.format(
            'sphinx' if lowercase else 'Sphinx')

        self.expected_md5_checksum = '8f55a6d4f87fc6d528120c5d1f983e98'

    def perform_md5_validations(self, validators):
        _get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz.md5',
            validators)

    def perform_sha1_validations(self, validators):
        _get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz.sha1',
            validators)

    def perform_primary_artifact_validations(self, validators):
        _get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz',
            validators)


def perform_package_not_cached_assertions(sphinx_helper):
    sphinx_helper.perform_md5_validations((_validate_404,))
    sphinx_helper.perform_sha1_validations((_validate_404,))
    sphinx_helper.perform_primary_artifact_validations(
        (partial(_validate_content_length, 2632059),
         partial(_validate_md5, '8f55a6d4f87fc6d528120c5d1f983e98'),)
    )


def perform_package_cached_assertions(sphinx_helper):
    sphinx_helper.perform_md5_validations((
        partial(_validate_text, sphinx_helper.expected_md5_checksum),
        partial(_validate_content_type, 'application/x-checksum'),
    ))

    sphinx_helper.perform_sha1_validations((_validate_404,))

    sphinx_helper.perform_primary_artifact_validations((
        partial(_validate_content_length, 2632059),
        partial(_validate_md5, sphinx_helper.expected_md5_checksum),
    ))


def perform_package_unavailable_assertions(sphinx_helper):
    sphinx_helper.perform_md5_validations((_validate_404,))
    sphinx_helper.perform_sha1_validations((_validate_404,))
    sphinx_helper.perform_primary_artifact_validations((_validate_404,))


def _assert_package_retrieval_behavior(lowercase):
    helper = SphinxHelper(lowercase=lowercase)

    perform_package_not_cached_assertions(helper)
    perform_package_cached_assertions(helper)

    with proxy_brought_down(fixture.proxy):
        perform_package_cached_assertions(helper)

        fixture.artif.flush_caches()
        perform_package_unavailable_assertions(helper)
