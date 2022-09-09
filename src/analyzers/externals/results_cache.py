import requests
from externals.utilities import check_connection


def post_results_cache(URI: str, username: str, claim_check: str, generation_time: float, data: str):
    params = {
        "claim_check": claim_check,
        "generation_time": int(generation_time),
        "username": username
    }

    resp = requests.post(URI + "/api/store_result", params=params, data=data)
    check_connection(resp, URI)

def post_status(URI: str, username: str, claim_check: str, status: float):
    params = {
        "claim_check": claim_check,
        "username": username
    }

    resp = requests.post(URI + "/api/update_status", params=params, data=str(status))
    check_connection(resp, URI)

def post_error(URI: str, username: str, claim_check: str, error: str):
    params = {
        "claim_check": claim_check,
        "username": username
    }

    if URI.find('FILE') == 0:
      print(" post error:", params, error)
      return
    resp = requests.post(URI + "/api/put_error", params=params, data=error)
    check_connection(resp, URI)