import argparse
import os
import numpy as np
import time
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

from common.mko import MKO, encodings
from externals import get_samples_array, post_error, post_results_cache, post_status


import time

def parse_args():
  parser = argparse.ArgumentParser(description='Train an MKO')
  parser.add_argument('--mko', nargs=1, dest='mko_filename', type=str, required=True, help='path to file for MKO')
  parser.add_argument('-i', nargs=1, dest='data_filename', type=str, required=True, help='path to file containing inputs')
  parser.add_argument('--n_bins', nargs=1, dest='n_bins', type=int, default=[0], required=False, help='number of bins in histogram')
  parser.add_argument('--n_samples', nargs=1, dest='n_samples', type=int, default=[0], required=False, help='number of samples to take')
  parser.add_argument('-u', nargs=1, dest='username', type=str, required=True, help='username for result_cache')
  parser.add_argument('--cc', nargs=1, dest='claim_check', type=str, required=True, help='claim_check for result_cache')
  parser.add_argument('--rc', nargs=1, dest="rc_url", type=str, required=True, help='url to result_cache server')
  return parser.parse_args()

def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return
    os.unlink(file_loc)

def cloudplot(mko_filename, data_filename, username, claim_check, rc_url, n_samples=100):

  def get_post_status_closure(rc_url, username, claim_check):
    def post_status_closure(status):
      post_status(rc_url, username, claim_check, status)
    return post_status_closure
  status_poster = get_post_status_closure(rc_url, username, claim_check)
  
  start_time = time.time()
  status_poster(0.0)

  if n_samples <= 0:
    n_samples = 100

  with open(mko_filename, 'r') as fd:
    mko_data = fd.read()
    fd.close()
  delete_file(mko_filename)
  mko = MKO.from_base64(mko_data)

  data_rows = np.loadtxt(data_filename)
  delete_file(data_filename)

  n_rows = data_rows.shape[0]
  n_inputs = len(mko.dataspec['inputs'])
  n_outputs = len(mko.dataspec['outputs'])
  if mko.dataspec["time_as_input"]: n_inputs += 1 
  inputs = data_rows[:,0:n_inputs]
  outputs = data_rows[:,n_inputs:]

  predict = np.empty((n_rows, n_outputs, n_samples))
  predict[:,:,:] = get_samples_array(username, mko_data, n_samples, inputs)

  matplotlib.use('agg')
  images = []
  for j in range(n_outputs):
    output_name = mko.dataspec['outputs'][j]
    fig = plt.figure(figsize=(5,5), dpi=100)
    for i in range(n_rows):
      known = outputs[i,j].repeat(n_samples)
      plt.scatter(known, predict[i,j,:], alpha=0.2, marker='o', color='r')
    ll = min(np.amin(known), np.amin(predict[:,j,:]))
    ul = max(np.amax(known), np.amax(predict[:,j,:]))
    plt.xlim((ll, ul))
    plt.ylim((ll, ul))
    plt.plot([ll, ul], [ll,ul], color='blue')
    plt.title(output_name)
    stream = BytesIO() 
    plt.savefig(stream, format="png", bbox_inches='tight')
    plt.close()
    stream.seek(0)
    image = encodings.encode_base64(stream.read())
    images.append(image)
    stream.close()

  data = encodings.b64encode_datatype(images)

  end_time = time.time()
  generation_time = max(1, int(end_time - start_time))

  try:
    post_results_cache(rc_url, username, claim_check, generation_time, data)
  except Exception as err:
    post_error(rc_url, username, claim_check, str(err))
    raise err

if __name__ == '__main__':
  args = vars(parse_args())
  mko_filename = args['mko_filename'][0]
  data_filename = args['data_filename'][0]
  username = args['username'][0]
  claim_check = args['claim_check'][0]
  rc_url = args['rc_url'][0]
  n_samples = args['n_samples'][0]

  cloudplot(mko_filename, data_filename, username, claim_check, rc_url, n_samples=100)
