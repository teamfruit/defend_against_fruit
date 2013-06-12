from time import sleep
import requests


def _assert_services_up(services):
    for s in services:
        s.block_until_up()


def _return_when_web_service_up(health_check_url, attempts=5):
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