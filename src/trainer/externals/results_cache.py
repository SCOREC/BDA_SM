import requests
from externals.utilities import check_connection


def post_result_cache(URI: str, username: str, claim_check: str, generation_time: float, mko_json: str):
    if URI.find('FILE') == 0:
      _, filename = URI.split(":")
      with open(filename, "w") as fd:
        fd.write(mko_json)
      return
    params = {
        "claim_check": claim_check,
        "generation_time": int(generation_time),
        "username": username
    }

    resp = requests.post(URI + "/api/store_result", params=params, data=mko_json)
    check_connection(resp, URI)

def post_status(URI: str, username: str, claim_check: str, status: float):
    params = {
        "claim_check": claim_check,
        "username": username
    }

    resp = requests.post(URI + "/update_status", params=params, data=str(status))
    check_connection(resp, URI)

def post_error(URI: str, username: str, claim_check: str, error: str):
    params = {
        "claim_check": claim_check,
        "username": username
    }

    if URI.find('FILE') == 0:
      print(" post error:", params, error)
      return
    resp = requests.post(URI + "/put_error", params=params, data=error)
    check_connection(resp, URI)