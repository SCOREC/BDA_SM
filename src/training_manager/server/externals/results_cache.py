import requests
from config.externals import Config as cfg
from exceptions import RCException

def get_new_claim_check(username: str, offset: int=0) -> str:
  new_claim_check_request = {"username": username}
  try:
    claim_check_URL = cfg.RESULTS_CACHE_BASE_URL+"/api/new_claim_check"
    rc_response = requests.get(claim_check_URL, params=new_claim_check_request)
    if rc_response.status_code != 200:
      raise RCException("Result cache did not issue claim check")
    claim_check = rc_response.json()['claim_check']
  except Exception as err:
    raise RCException(err)

  return claim_check

def post_results_cache(username: str, claim_check: str, generation_time: float, mko_json: str):
    params = {
        "claim_check": claim_check,
        "generation_time": int(generation_time),
        "username": username
    }

    store_url = cfg.RESULTS_CACHE_BASE_URL+"/api/store_result"
    rc_response = requests.post(store_url, params=params, data=mko_json)
    if rc_response.status_code != 200:
      raise RCException(f"Result cache could not store result for claimcheck {claim_check}")