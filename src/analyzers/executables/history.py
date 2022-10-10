import argparse
import os
import numpy as np
import time
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

from common.mko import MKO
from common.utilities import encodings
from externals import post_error, post_results_cache, post_status


import time

def parse_args():
  parser = argparse.ArgumentParser(description='Train an MKO')
  parser.add_argument('--mko', nargs=1, dest='mko_filename', type=str, required=True, help='path to file for MKO')
  parser.add_argument('-u', nargs=1, dest='username', type=str, required=True, help='username for result_cache')
  parser.add_argument('--cc', nargs=1, dest='claim_check', type=str, required=True, help='claim_check for result_cache')
  parser.add_argument('--rc', nargs=1, dest="rc_url", type=str, required=True, help='url to result_cache server')
  return parser.parse_args()

def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return
    os.unlink(file_loc)

def history(mko_filename, username, claim_check, rc_url):

  def get_post_status_closure(rc_url, username, claim_check):
    def post_status_closure(status):
      post_status(rc_url, username, claim_check, status)
    return post_status_closure
  status_poster = get_post_status_closure(rc_url, username, claim_check)
  
  start_time = time.time()
  status_poster(0.0)

  with open(mko_filename, 'r') as fd:
    mko_data = fd.read()
    fd.close()
  delete_file(mko_filename)
  mko = MKO.from_base64(mko_data)

  loss_history = mko._hypers["loss_history"]
  lr_history = mko._hypers["lr_history"]
  epochs = [float(x + 1) for x in range(len(loss_history))]


  matplotlib.use('agg')
  fig, ax1 = plt.subplots(figsize=(5,5), dpi=100)
  color = "tab:red"
  ax1.semilogy(epochs, loss_history, label="loss", lw=2.0, color=color)
  ax1.set_xlabel("Epochs")
  ax1.set_ylabel("Loss", color=color)
  ax1.tick_params(axis='y', labelcolor=color)
  ax2 = ax1.twinx()
  color = "tab:blue"
  ax2.semilogy(epochs, lr_history, label="learning rate", lw=2.0, color=color)
  ax2.set_ylabel("Learning rate", color=color)
  ax2.tick_params(axis='y', labelcolor=color)
  plt.legend()


  stream = BytesIO() 
  plt.savefig(stream, format="png", bbox_inches='tight')
  stream.seek(0)

  data = encodings.encode_base64(stream.read())
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
  username = args['username'][0]
  claim_check = args['claim_check'][0]
  rc_url = args['rc_url'][0]

  history(mko_filename, username, claim_check, rc_url)
