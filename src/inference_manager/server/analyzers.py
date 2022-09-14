import os
import subprocess
import requests
import tempfile 
import numpy as np
from server.config import AnalyzersConfig as cfg

def get_new_claim_check(username: str, offset: int=0) -> str:
  new_claim_check_request = {"username": username}
  try:
    claim_check_URL = cfg.RESULTS_CACHE_BASE_URL+"/api/new_claim_check"
    rc_response = requests.get(claim_check_URL, params=new_claim_check_request)
    if rc_response.status_code != 200:
      raise Exception("Result cache did not issue claim check")
    claim_check = rc_response.json()['claim_check']
  except Exception as err:
    raise Exception(err)
  return claim_check

def save_file(data):
  f = tempfile.NamedTemporaryFile("w", delete=False)
  f.write(str(data))
  f.close()
  return f.name

def save_array(data):
  f = tempfile.NamedTemporaryFile("w", delete=False)
  np.savetxt(fname=f, X=data)
  f.close()
  return f.name



def get_histogram(mko, inputs, username, n_samples, n_bins) -> str:
  claim_check = get_new_claim_check(username)
  mko_file = save_file(mko)
  inputs_file = save_file(inputs)
  mod_env = dict(os.environ)
  mod_env.update({'PYTHONPATH' : "."})
  EXECUTABLE_STRING_LIST = [
    cfg.PYTHON_EXECUTABLE,
    "executables/histogram.py",
    "-u",
    username,
    "--cc",
    claim_check,
    "--rc",
    cfg.RESULTS_CACHE_BASE_URL,
    "--mko",
    mko_file,
    "-i",
    inputs_file,
    "--n_bins",
    str(n_bins),
    "--n_samples",
    str(n_samples)
    ]
  print(EXECUTABLE_STRING_LIST)
  subprocess.Popen(
    EXECUTABLE_STRING_LIST,
    cwd=cfg.EXECUTABLE_WORKING_DIRECTORY,
    env=mod_env
    )
  
  return claim_check

def get_cloudplot(mko, data, username, n_samples) -> str:
  claim_check = get_new_claim_check(username)
  mko_file = save_file(mko)
  data_file = save_array(data)
  mod_env = dict(os.environ)
  mod_env.update({'PYTHONPATH' : "."})
  EXECUTABLE_STRING_LIST = [
    cfg.PYTHON_EXECUTABLE,
    "executables/cloudplot.py",
    "-u",
    username,
    "--cc",
    claim_check,
    "--rc",
    cfg.RESULTS_CACHE_BASE_URL,
    "--mko",
    mko_file,
    "-i",
    data_file,
    "--n_samples",
    str(n_samples)
    ]
  print(EXECUTABLE_STRING_LIST)
  subprocess.Popen(
    EXECUTABLE_STRING_LIST,
    cwd=cfg.EXECUTABLE_WORKING_DIRECTORY,
    env=mod_env
    )
  
  return claim_check