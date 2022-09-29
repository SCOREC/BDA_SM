from flask import Blueprint
from flask import request, abort
from flask.wrappers import Response

import json
from subprocess import Popen, PIPE, STDOUT

import server.analyzers
import common.utilities.encodings as encodings
from server.config import AnalyzersConfig as cfg

AnalyzersResource = Blueprint('Analyzers', __name__)
sampler_base_url = str(cfg.SAMPLER_BASE_URL).rstrip('/ ')

@AnalyzersResource.route('/histogram', methods=['POST'])
def histogram():
  try:
    data = request.data
    data = json.loads(data)['data']
    username = data.get("username")
    mko = data.get('mko')
    inputs = encodings.b64decode_datatype(data.get('inputs'))
    n_bins = data.get('n_bins', 0)
    n_samples = data.get('n_samples', 0)
    claim_check = server.analyzers.get_histogram(mko, inputs, username, n_samples=n_samples, n_bins=n_bins)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)
  return ({"claim_check": claim_check}, 200)

@AnalyzersResource.route('/cloudplot', methods=['POST'])
def cloudplot():
  try:
    data = request.data
    data = json.loads(data)['data']
    username = data.get("username")
    mko = data.get('mko')
    data_table = encodings.b64decode_datatype(data.get('data_table'))
    n_samples = data.get('n_samples', 0)
    claim_check = server.analyzers.get_cloudplot(mko, data_table, username, n_samples=n_samples)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)
  return ({"claim_check": claim_check}, 200)

@AnalyzersResource.route('/integrate', methods=['POST'])
def integrate():
  try:
    data = request.data
    data = json.loads(data)['data']
    username = data.get("username")
    mko = data.get('mko')
    inputs = encodings.b64decode_datatype(data.get('inputs'))
    function_table = encodings.b64decode_datatype(data.get('function'))
    n_samples = data.get('n_samples', 0)
    claim_check = server.analyzers.get_integration(
      mko=mko,
      inputs=inputs,
      username=username,
      n_samples=n_samples,
      function_table=function_table
      )
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)
  return ({"claim_check": claim_check}, 200)