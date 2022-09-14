import requests
import json
from externals.config import ExternalsConfig as cfg
from common.mko import MKO, encodings
import numpy as np

def get_samples(username, mko_data, n_samples : int, inputs : list, as_csv=False, precision=8):
  data =  {
      "username" : username,
      "mko" : mko_data,
      "inputs": inputs,
      "n_samples" : n_samples,
      "as_csv" : as_csv,
      "precision" : precision,
    }
  data = json.dumps({'data' : data})
  response = requests.post(cfg.sampler_url,  data=data)
  string = json.loads(response.content)['outputs']
  if as_csv:
    return string
  else:
    return encodings.b64decode_datatype(string)


def get_samples_array(username, mko_data, n_samples : int, inputs : np.ndarray, as_csv=False, precision=8):
  data =  {
      "username" : username,
      "mko" : mko_data,
      "inputs": encodings.b64encode_datatype(inputs),
      "n_samples" : n_samples,
      "as_csv" : as_csv,
      "precision" : precision
    }
  data = json.dumps({'data' : data})
  response = requests.post(cfg.sampler_array_url,  data=data)
  string = json.loads(response.content)['outputs']
  if as_csv:
    return string
  else:
    return encodings.b64decode_datatype(string)

