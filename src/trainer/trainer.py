import argparse
import os
import pandas as pd
import numpy as np
import json
import time

import externals
from common.mko import MKO
from common.ml import parse_json_model_structure, compile_model, fit_model, autocalibrate_model

import time

def parse_args():
  parser = argparse.ArgumentParser(description='Train an MKO')
  parser.add_argument('--mko', nargs=1, dest='mko_filename', type=str, required=True, help='path to file for MKO')
  parser.add_argument('-u', nargs=1, dest='username', type=str, required=True, help='username for result_cache')
  parser.add_argument('--cc', nargs=1, dest='claim_check', type=str, required=True, help='claim_check for result_cache')
  parser.add_argument('--rc', nargs=1, dest="rc_url", type=str, required=True, help='url to result_cache server')
  parser.add_argument('--token', nargs=1, dest="smip_token", type=str, required=True, help='token for smip server')
  parser.add_argument('--ac', dest="autocalibrate", default=False, action='store_true', help='Automatically calibrate to desired mu')
  parser.add_argument('--point', nargs=1, dest="cp_loc", type=str, required=False, default="", help='filename with inputs at which to calibrates mu')
  parser.add_argument('--mu', nargs=1, dest="desired_mu", type=float, required=False, default=1.0, help='mu to calibrate to (normalized)')
  parser.add_argument('--ac_index', nargs=1, dest="ac_index", type=int, required=False, default=0, help='index of output being calibrated')

  return parser.parse_args()

def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return
    os.unlink(file_loc)

def get_data_from_fetcher(mko : 'MKO', smip_token : str):
  if mko.series_type == 'time':
    ids = mko.dataspec['inputs'] + mko.dataspec['outputs']
    query = mko.dataspec['query_json']
    query["attrib_id_list"] = ids
    smip_url = mko.dataspec['data_location']

    auth = {
        'smip_token' : smip_token,
        'smip_url'   : smip_url
    }

    fetcher_data = externals.query_fetcher_ts(json.dumps(query), json.dumps(auth))
    df = pd.read_json(fetcher_data)
    if mko.dataspec['time_as_input']:
      input_indices = ['ts'] + mko.dataspec['inputs']
    else:
      input_indices = mko.dataspec['inputs']
    output_indices = mko.dataspec['outputs']
    return df[input_indices], df[output_indices]
  elif mko.series_type == 'lot':
    query = mko.dataspec['query_json']
    query["attrib_id"] = mko.dataspec['attrib_id']
    smip_url = mko.dataspec['data_location']
    auth = {
        'smip_token' : smip_token,
        'smip_url'   : smip_url
    }
    fetcher_data = externals.query_fetcher_ls(json.dumps(query), json.dumps(auth))
    df = pd.read_json(fetcher_data)
    if not mko.dataspec['query_json']['all_lots']:
      df.sort_index(inplace=True)
      try:
        start_lot = int(float(mko.dataspec['start_lot']))
        end_lot = int(float(mko.dataspec['end_lot']))
        df = df.loc[start_lot:end_lot]
      except:
        pass
    return df[mko.dataspec['inputs']], df[mko.dataspec['outputs']]
  else:
    raise Exception("This can't happen")
  
def prepare_training_data(mko, smip_token):
  inputs, outputs = get_data_from_fetcher(mko, smip_token)
  nx = inputs.shape[0]
  inputs, outputs = same_shuffle(inputs.to_numpy(), outputs.to_numpy(), axis=-1)
  inputs = mko.normalize_training_inputs(inputs)
  outputs = mko.normalize_training_outputs(outputs)

  p = int( float(nx) * mko.hypers['train_percent'] )
  X_train = inputs [ :p, :]
  Y_train = outputs[ :p, :]
  X_test  = inputs [p: , :]
  Y_test  = outputs[p: , :]
  return X_train, Y_train, X_test, Y_test

def prepare_mko_model(mko : MKO):
  n_inputs = len(mko.dataspec['inputs'])
  if mko.dataspec["time_as_input"]: n_inputs += 1
  n_outputs = len(mko.dataspec['outputs'])
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


def trainer(mko_filename, username, claim_check, rc_url, smip_token,
            autocalibrate=False, cp_loc=None, desired_mu=None, index=None):

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

  X_train, Y_train, X_test, Y_test = prepare_training_data(mko, smip_token)

  try:
    mko = prepare_mko_model(mko)

    mko._model, mko._hypers['loss'] = fit_model(
      mko._model,
      X_train, Y_train,
      X_test, Y_test,
      mko.hypers,
      status_poster
      )
    mko.set_trained()

    if autocalibrate:
      if len(cp_loc) > 0:
        with open(cp_loc, "r") as fd:
          calibration_point = fd.read()
          fd.close()
        calibration_point = np.fromstring(calibration_point, sep=",")
        delete_file(cp_loc)
      else:
        calibration_point = X_train.mean(axis=0)

      new_model, rho = autocalibrate_model(
        mko._model,
        X_train, Y_train,
        mko.hypers, mko.topology,
        status_poster,
        calibration_point,
        desired_mu=desired_mu,
        index=index
      )
      mko._model = new_model
    end_time = time.time()
    generation_time = max(1, int(end_time - start_time))
  except Exception as err:
    externals.post_error(rc_url, username, claim_check, str(err))
    raise err

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
  autocalibrate = args.get('autocalibrate',False)

  if autocalibrate:
    cp_loc = args.get('cp_loc',[""])[0]
    desired_mu = args.get('desired_mu', [1.0])[0]
    index = args.get('ac_index', [0])[0]
    trainer(mko_filename, username, claim_check, rc_url, smip_token,
      autocalibrate=True, cp_loc=cp_loc,
      desired_mu=desired_mu, index=index)
  else:
    trainer(mko_filename, username, claim_check, rc_url, smip_token)
