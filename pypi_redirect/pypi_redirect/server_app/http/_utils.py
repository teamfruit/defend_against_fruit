import requests


def http_get(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text
