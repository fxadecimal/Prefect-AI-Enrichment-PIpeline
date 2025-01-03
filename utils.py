import requests
import time


def download(url, path, headers=None, params=None, sleep=5, **kwargs):
    print(f"Downloading {url}...")
    response = requests.get(url, headers=headers, params=params, **kwargs)

    with open(path, "wb") as f:
        f.write(response.content)

    if sleep:
        time.sleep(sleep)

    return response
