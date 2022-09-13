import argparse
import os
import pandas as pd
import numpy as np
import json
import time

import externals
from common.mko import MKO
from common.ml import parse_json_model_structure, compile_model, fit_model

import time

def parse_args():
  parser = argparse.ArgumentParser(description='Train an MKO')
  parser.add_argument('--mko', nargs=1, dest='mko_filename', type=str, required=True, help='path to file for MKO')
  parser.add_argument('-u', nargs=1, dest='username', type=str, required=True, help='username for result_cache')
  parser.add_argument('--cc', nargs=1, dest='claim_check', type=str, required=True, help='claim_check for result_cache')
  parser.add_argument('--rc', nargs=1, dest="rc_url", type=str, required=True, help='url to result_cache server')
  parser.add_argument('--token', nargs=1, dest="smip_token", type=str, required=True, help='token for smip server')
  return parser.parse_args()

def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return
    os.unlink(file_loc)

def get_data_from_fetcher(mko : 'MKO', smip_token : str):
    ids = mko.dataspec['x_tags'] + mko.dataspec['y_tags']
    query = mko.dataspec['query_json']
    query["attrib_id_list"] = ids
    smip_url = mko.dataspec['data_location']

    auth = {
        'smip_token' : smip_token,
        'smip_url'   : smip_url
    }

    fetcher_data = externals.query_fetcher(json.dumps(query), json.dumps(auth))
    df = pd.read_json(fetcher_data)
    if mko.dataspec['time_as_input']:
      input_indices = ['ts'] + mko.dataspec['x_tags']
    else:
      input_indices = mko.dataspec['x_tags']
    output_indices = mko.dataspec['y_tags']
    return df[input_indices].to_numpy(), df[output_indices].to_numpy()
  
def prepare_mko_model(mko):
  n_inputs = len(mko.dataspec['x_tags'])
  if mko.dataspec["time_as_input"]: n_inputs += 1
  n_outputs = len(mko.dataspec['y_tags'])
  model = parse_json_model_structure((n_inputs,), mko._model_name, mko.topology, n_outputs)
  mko._model = compile_model(model, mko.hypers)
  mko.set_compiled(True)
  mko.parameterize_model()
  return mko

def same_shuffle(a, b, axis=0):
  seed = int(1000000*np.random.uniform())
  rng = np.random.default_rng(seed)
  rng.shuffle(a, axis=axis)
  rng = np.random.default_rng(seed)
  rng.shuffle(b, axis=axis)
  return a, b


def trainer(mko_filename, username, claim_check, rc_url, smip_token):

  def get_post_status_closure(rc_url, username, claim_check):
    def post_status_closure(status):
      externals.post_status(rc_url, username, claim_check, status)
    return post_status_closure
  status_poster = get_post_status_closure(rc_url, username, claim_check)
  

  start_time = time.time()
  status_poster(0.0)

  with open(mko_filename, 'r') as fd:
    mko_data = fd.read()
    fd.close()
  delete_file(mko_filename)

  mko = MKO.from_base64(mko_data)
  
  try:
    inputs, outputs = get_data_from_fetcher(mko, smip_token)
    mko = prepare_mko_model(mko)
  except Exception as err:
    externals.post_error(rc_url, username, claim_check, str(err))
    raise err

  nx = inputs.shape[0]
  ny = outputs.shape[0]
  inputs, outputs = same_shuffle(inputs, outputs, axis=0)
  inputs = mko.normalize_training_inputs(inputs)
  outputs = mko.normalize_training_outputs(outputs)

  p = int( float(nx) * mko.hypers['train_percent'] )
  X_train = inputs [ :p, :]
  Y_train = outputs[ :p, :]
  X_test  = inputs [p: , :]
  Y_test  = outputs[p: , :]

  try:
    mko._model, mko._hypers['loss'] = fit_model(
      mko._model,
      X_train, Y_train,
      X_test, Y_test,
      mko.hypers,
      status_poster
      )
    mko.set_trained()
  except Exception as err:
    externals.post_error(rc_url, username, claim_check, str(err))
    raise err

  end_time = time.time()
  generation_time = max(1, int(end_time - start_time))

  try:
    externals.post_results_cache(rc_url, username, claim_check, generation_time, mko.b64)
  except Exception as err:
    externals.post_error(rc_url, username, claim_check, str(err))
    raise err
  

if __name__ == '__main__':
  args = vars(parse_args())
  mko_filename = args.get('mko_filename')[0]
  username = args.get('username')[0]
  claim_check = args.get('claim_check')[0]
  rc_url = args.get('rc_url')[0]
  smip_token = args.get('smip_token')[0]

  trainer(mko_filename, username, claim_check, rc_url, smip_token)
