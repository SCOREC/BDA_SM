import argparse
import os
import math
from scipy.interpolate import RegularGridInterpolator
import numpy as np
import time
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

from common.mko import MKO
from common.utilities import encodings
from externals import get_samples, post_error, post_results_cache, post_status


import time

def parse_args():
  parser = argparse.ArgumentParser(description='Train an MKO')
  parser.add_argument('--mko', nargs=1, dest='mko_filename', type=str, required=True,
    help='path to file for MKO')
  parser.add_argument('-i', nargs=1, dest='inputs_filename', type=str, required=True,
    help='path to file containing inputs')
  parser.add_argument('--function', nargs=1, dest='function_filename', type=str, required=True,
    help='file with function to integrate')
  parser.add_argument('--n_samples', nargs=1, dest='n_samples', type=int, default=[0], required=False,
    help='number of samples to take')
  parser.add_argument('-u', nargs=1, dest='username', type=str, required=True,
    help='username for result_cache')
  parser.add_argument('--cc', nargs=1, dest='claim_check', type=str, required=True,
    help='claim_check for result_cache')
  parser.add_argument('--rc', nargs=1, dest="rc_url", type=str, required=True,
    help='url to result_cache server')
  return parser.parse_args()

def table_to_dims(table : np.ndarray):
  dims = [0] * table.shape[1]
  def increasing_stride_length(tab):
    array = tab[:]
    last = array[0]
    stride = 1
    for val in array[1:]:
      if math.isclose(val, last) or val < last:
        continue
      else:
        last = val
        stride += 1
    return stride
  stride = 1
  for i in range(table.shape[1]-1, -1, -1):
    new_stride = increasing_stride_length(table[::stride,i])
    dims[i] = new_stride
    stride = stride * new_stride
  return dims

def table_to_gridlines(table):
  dims = table_to_dims(table)
  gridlines = [''] * len(dims)
  stride = 1
  for i in range(len(dims)):
    col = len(dims) - i - 1
    dim = dims[col]
    gridlines[col] = table[0:stride*dim:stride, col]
    stride = stride * dim
  return gridlines


def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return
    os.unlink(file_loc)

def integrator(mko_filename, inputs_filename, username, claim_check, rc_url, function_filename, n_samples=2000):

  def get_post_status_closure(rc_url, username, claim_check):
    def post_status_closure(status):
      post_status(rc_url, username, claim_check, status)
    return post_status_closure
  status_poster = get_post_status_closure(rc_url, username, claim_check)
  
  start_time = time.time()
  status_poster(0.0)

  if n_samples <= 0:
    n_samples = 2000

  with open(mko_filename, 'r') as fd:
    mko_data = fd.read()
    fd.close()
  delete_file(mko_filename)
  mko = MKO.from_base64(mko_data)

  inputs = np.loadtxt(inputs_filename)
  delete_file(inputs_filename)

  table = np.loadtxt(function_filename)
  delete_file(function_filename)
  gridlines = table_to_gridlines(table[:,:-1])
  data = table[:,-1]
  interp = RegularGridInterpolator(gridlines, data)
  samples = get_samples(username, mko_data, n_samples, inputs.tolist())

  integral = np.sum(interp(samples)) / float(n_samples)

  end_time = time.time()
  generation_time = max(1, int(end_time - start_time))

  try:
    post_results_cache(rc_url, username, claim_check, generation_time, str(integral))
  except Exception as err:
    post_error(rc_url, username, claim_check, str(err))
    raise err

if __name__ == '__main__':
  args = vars(parse_args())
  mko_filename = args['mko_filename'][0]
  inputs_filename = args['inputs_filename'][0]
  function_filename = args['function_filename'][0]
  username = args['username'][0]
  claim_check = args['claim_check'][0]
  rc_url = args['rc_url'][0]
  n_samples = args['n_samples'][0]

  integrator(mko_filename, inputs_filename, username, claim_check, rc_url, function_filename, n_samples)
