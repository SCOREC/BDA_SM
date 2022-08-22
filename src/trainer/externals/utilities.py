import requests
from externals.exceptions import ConnectionException

def check_connection(resp: requests.Response, URI: str):
    if resp.status_code != 200:
        raise ConnectionException(URI, resp.text)