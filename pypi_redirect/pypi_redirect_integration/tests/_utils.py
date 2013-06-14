from time import sleep
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