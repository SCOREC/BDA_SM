from operator import sub
import sys
import subprocess
import requests
import tempfile 
from server.config import TrainerConfig as cfg
import server.trainer.defaults as defaults
import json

from server.trainer import errors

def get_new_claim_check(username: str, offset: int=0) -> str:
  new_claim_check_request = {"username": username}
  try:
    claim_check_URL = cfg.RESULTS_CACHE_URL+"/api/new_claim_check"
    rc_response = requests.get(claim_check_URL, params=new_claim_check_request)
    if rc_response.status_code != 200:
      raise errors.RCException("Result cache did not issue claim check")
    claim_check = rc_response.json()['claim_check']
  except Exception as err:
    raise errors.RCException(err)

  return claim_check

def save_file(data):
  f = tempfile.NamedTemporaryFile("w", delete=False)
  f.write(data)
  f.close()
  return f.name


def create_mko(model_name: str, username: str) -> str:
  claim_check = get_new_claim_check(username)
  subprocess.Popen([
    *cfg.EXECUTABLE_NAME,
    username,
    claim_check,
    cfg.RESULTS_CACHE_URL,
    "--create",
    "--name", model_name,
    "--delete",
    ],
    cwd=cfg.EXECUTABLE_WORKING_DIRECTORY)
  return claim_check

def fill_mko(username: str, model_name: str, mko: str, dataspec_r: dict, topology_r: list=[], hypers_r:dict={} ) -> str:

  dataspec = defaults.dataspec
  for key in dataspec_r.keys():
    dataspec[key] = dataspec_r[key]
  if "REQUIRED" in dataspec.values():
    raise errors.InputException("Required value not in data specification")
  if 'n_outputs' in dataspec:
    n_outputs = dataspec['n_outputs']
  else:
    n_outputs = len(dataspec["y_tags"])

  if len(topology_r) > 0:
    topology = topology_r
  else:
    topology = defaults.topology
    topology[-1]['units'] = n_outputs

  hypers = defaults.hypers
  for key in hypers_r.keys():
    hypers[key] = hypers_r[key]
  if "REQUIRED" in hypers.values():
    raise errors.InputException("Required value not in hyper parameter specification")

  params = defaults.stub
  params['data'] = dataspec  # type: ignore
  params['topology'] = topology  # type: ignore
  params['hyper_params'] = hypers  # type: ignore

  params = json.dumps(params)
  add_loc = save_file(params)
  mko_loc = save_file(mko)

  claim_check = get_new_claim_check(username, 10)
  subprocess.Popen([
    *cfg.EXECUTABLE_NAME,
    username,
    claim_check,
    cfg.RESULTS_CACHE_URL,
    "-f",
    mko_loc,
    "--add",
    "ALL",
    add_loc
    ],
    cwd=cfg.EXECUTABLE_WORKING_DIRECTORY
  )
  return claim_check


def train_mko(username: str, model_name: str, mko: str, smip_token : str, smip_url : str) -> str:
  claim_check = get_new_claim_check(username)
  mko_loc = save_file(mko)
  EXECUTABLE_STRING_LIST = [
    *cfg.EXECUTABLE_NAME,
    username,
    claim_check,
    cfg.RESULTS_CACHE_URL,
    "--train",
    "--name", model_name,
    "--delete",
    "-f",
    mko_loc,
    "--smip_token",
    smip_token,
    "--smip_url",
    smip_url
    ]
  print(EXECUTABLE_STRING_LIST)
  subprocess.Popen(EXECUTABLE_STRING_LIST, cwd=cfg.EXECUTABLE_WORKING_DIRECTORY)
  
  return claim_check
