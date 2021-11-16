import requests


def fetch(*, url, headers):
    response = requests.get(url, headers=headers)
    return response.json()
