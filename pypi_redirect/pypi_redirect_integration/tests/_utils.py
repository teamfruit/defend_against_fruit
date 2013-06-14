from functools import partial
from time import sleep
from nose.tools import eq_
import requests


def return_when_web_service_up(health_check_url, attempts=5):
    while True:
        try:
            response = requests.get(health_check_url)
            response.raise_for_status()
        except requests.RequestException:
            pass
        else:
            break

        if attempts <= 0:
            raise AssertionError(
                'Failed to connect to {}'.format(health_check_url))

        attempts -= 1
        sleep(1)


def return_when_web_service_down(health_check_url, attempts=5):
    while True:
        try:
            response = requests.get(health_check_url)
            response.raise_for_status()
        except requests.RequestException:
            break

        if attempts <= 0:
            raise AssertionError(
                'Still connected to {}'.format(health_check_url))

        attempts -= 1
        sleep(1)


def find_all_links(html_root):
    return html_root.xpath(".//a")


def get_sphinx_from_url_and_validate(
        get_url_fn,
        checksum_ext='',
        expect_package_not_found=False,
        expect_md5_not_found=False,
        lowercase_package=False):

    package = 'sphinx' if lowercase_package else 'Sphinx'
    filename = 'Sphinx-1.1.3.tar.gz' + checksum_ext
    expected_checksum = '8f55a6d4f87fc6d528120c5d1f983e98'

    validators = {
        # Non-checksum file validators
        '': (
            _validate_404,
        ) if expect_package_not_found else (
            partial(_validate_content_length, 2632059),
            partial(_validate_md5, expected_checksum),
        ),

        # MD5 validators
        '.md5': (
            _validate_404,
        ) if expect_md5_not_found else (
            partial(_validate_text, expected_checksum),
            partial(_validate_content_type, 'application/x-checksum'),
        ),

        # SHA1 validators
        '.sha1': (
            _validate_404,
        ),
    }

    # Use the specified validator. If an unrecognized extension is used, use
    # the 404 validator.
    validate_fn_list = validators.get(checksum_ext, (_validate_404,))

    _get_url_and_validate(
        get_url_fn=get_url_fn,
        package=package,
        filename=filename,
        validate_fn_list=validate_fn_list)


def assert_sphinx_packages(listed_packages):
    assert 'Sphinx-1.1-py2.7.egg' in listed_packages
    assert 'Sphinx-1.1-py2.7.egg.md5' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz.md5' in listed_packages


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


def _get_url_and_validate(get_url_fn, package, filename, validate_fn_list):
    result = get_url_fn(
        path='python/{}/{}'.format(package, filename))

    for v in validate_fn_list:
        v(result=result)
