from functools import partial
from nose.tools import eq_


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


class SphinxHelper(object):
    def __init__(self, get_path_fn, lowercase=False):
        self._package_prefix = 'python/{}/'.format(
            'sphinx' if lowercase else 'Sphinx')

        self.get_path_fn = get_path_fn
        self.expected_md5_checksum = '8f55a6d4f87fc6d528120c5d1f983e98'

    def __get_path_and_perform_validations(self, path, validate_fn_list):
        result = self.get_path_fn(path)

        for v in validate_fn_list:
            v(result)

    def perform_md5_validations(self, validators):
        self.__get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz.md5',
            validators)

    def perform_sha1_validations(self, validators):
        self.__get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz.sha1',
            validators)

    def perform_primary_artifact_validations(self, validators):
        self.__get_path_and_perform_validations(
            self._package_prefix + '/Sphinx-1.1.3.tar.gz',
            validators)


def perform_package_not_cached_assertions(sphinx_helper):
    sphinx_helper.perform_md5_validations((_validate_404,))
    sphinx_helper.perform_sha1_validations((_validate_404,))
    sphinx_helper.perform_primary_artifact_validations(
        (partial(_validate_content_length, 2632059),
         partial(_validate_md5, '8f55a6d4f87fc6d528120c5d1f983e98'),)
    )


def perform_package_cached_assertions(
        sphinx_helper,
        expect_artifactory_specific_headers):

    sphinx_helper.perform_md5_validations((
        partial(_validate_text, sphinx_helper.expected_md5_checksum),
        partial(_validate_content_type, 'application/x-checksum'),
    ))

    sphinx_helper.perform_sha1_validations((_validate_404,))

    primary_artifact_validators = [
        partial(_validate_content_length, 2632059)]

    if expect_artifactory_specific_headers:
        primary_artifact_validators.append(
            partial(_validate_md5, sphinx_helper.expected_md5_checksum))

    sphinx_helper.perform_primary_artifact_validations(
        primary_artifact_validators)


def perform_package_unavailable_assertions(sphinx_helper):
    sphinx_helper.perform_md5_validations((_validate_404,))
    sphinx_helper.perform_sha1_validations((_validate_404,))
    sphinx_helper.perform_primary_artifact_validations((_validate_404,))
