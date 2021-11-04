import requests
from src.exceptions import ConnectionException

def check_connection(resp, URI):
    if resp != 200:
        raise ConnectionException(URI)

def query_fetcher(URI, args):
    resp = requests.get(URI)
    check_connection(resp, URI)
    return resp.text

def post_result_cache(URI, username, claim_check, generation_time, mko):
    params = {
        "claim_check": claim_check,
        "generation_time": generation_time,
        "username": username
    }

    resp = requests.post(URI, params=params, data=mko)
    check_connection(resp, URI)