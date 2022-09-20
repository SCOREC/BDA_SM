import subprocess
import requests
import tempfile 
from server.config import ExternalsConfig as cfg
import server.curator.defaults as defaults

import server.exceptions as exceptions

def get_new_claim_check(username: str, offset: int=0) -> str:
  new_claim_check_request = {"username": username}
  try:
    claim_check_URL = cfg.RESULTS_CACHE_BASE_URL+"/api/new_claim_check"
    rc_response = requests.get(claim_check_URL, params=new_claim_check_request)
    if rc_response.status_code != 200:
      raise exceptions.RCException("Result cache did not issue claim check")
    claim_check = rc_response.json()['claim_check']
  except Exception as err:
    raise exceptions.RCException(err)

  return claim_check

def save_file(data):
  f = tempfile.NamedTemporaryFile("w", delete=False)
  f.write(data)
  f.close()
  return f.name


def train_mko(username: str, model_name: str, mko: str, smip_token : str, smip_url : str,
              autocalibrate=False, calibration_point="", desired_mu=1.0, index=0,
  ) -> str:
  claim_check = get_new_claim_check(username)
  mko_loc = save_file(mko)
  EXECUTABLE_STRING_LIST = [
    *cfg.EXECUTABLE_NAME,
    "-u", username,
    "--cc", claim_check,
    "--rc", cfg.RESULTS_CACHE_BASE_URL,
    "--mko", mko_loc,
    "--token", smip_token,
    ]
  if autocalibrate:
    if len(calibration_point) > 0:
      calibration_point_loc = save_file(calibration_point)
    else:
      calibration_point_loc = ""
    EXECUTABLE_STRING_LIST = EXECUTABLE_STRING_LIST + [
      "--ac",
      "--point", str(calibration_point_loc),
      "--mu", str(desired_mu),
      "--ac_index", str(index),
    ]
  print(EXECUTABLE_STRING_LIST)
  subprocess.Popen(EXECUTABLE_STRING_LIST, cwd=cfg.EXECUTABLE_WORKING_DIRECTORY)
  
  return claim_check
