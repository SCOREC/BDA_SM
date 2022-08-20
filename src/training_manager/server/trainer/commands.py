from re import A
import subprocess
import requests
from server.config import TrainerConfig as cfg

from server.trainer import errors

def get_new_claimcheck(username: str) -> str:
  new_claim_check_request = {"username": username}
  try:
    rc_response = requests.post(cfg.RESULTS_CACHE_URI + "/newClaimCheck",
      data={"query": new_claim_check_request})
    if rc_response.status_code != 200:
      raise errors.RCException("Result cache did not issue claim check")
    claim_check = rc_response.json()['claimcheck']
  except Exception as err:
    raise errors.RCException(err)

  return claim_check

def create_mko(model_name: str, username: str) -> str:
  claim_check = get_new_claimcheck(username)
  subprocess.Popen([
    *cfg.EXECUTABLE_PATH,
    username,
    claim_check,
    cfg.RESULTS_CACHE_URI,
    "--create",
    "--name", model_name,
    "--cleanup",
    ]
  )
  return claim_check

