from time import sleep
from pypi_redirect.server_app import index_parser
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


def assert_sphinx_packages(listed_packages):
    assert 'Sphinx-1.1-py2.7.egg' in listed_packages
    assert 'Sphinx-1.1-py2.7.egg.md5' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz' in listed_packages
    assert 'Sphinx-1.1.3.tar.gz.md5' in listed_packages


def parse_listing(url):
    result = requests.get(url)
    result.raise_for_status()

    html_str = result.text

    # Our index_parser.parse is very well unit-tested.
    rows = index_parser.parse(
        base_url=url,
        package_path='',
        html_str=html_str,
        strict_html=False,
        find_links_fn=find_all_links)

    return tuple(rows.iterkeys())
