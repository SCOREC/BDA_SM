from flask import request, abort
from flask.wrappers import Response
from server.sampler import sample_inputs, sample_inputs_array
import json
from flask import Blueprint

import common.mko.encodings as encodings

bp = Blueprint('api',__name__)

def get_input(field, args, return_none=False):
    if field not in args:
        if not return_none:
            abort(Response("'{}' not in args".format(field), 400))
        else:
            return None

    return args[field]

@bp.route("/sample", methods=["POST"])
def sample():
  try:
    data = request.data
    data = json.loads(data)['data']
    mko_data = data.get("mko")
    inputs = data.get("inputs")
    n_samples = int(data.get("n_samples"))
    as_csv = (data.get('as_csv', "True") == "True")
    precision = int(data.get('precision', 8))

    outputs = sample_inputs(mko_data, inputs, n_samples, as_csv, precision)
    response_text = {
        "outputs": outputs
    }
    return Response(json.dumps(response_text), 200)
  except Exception as err:
    return Response("Sampler error", 409)

@bp.route("/sampleArray", methods=["POST"])
def sample_array():
  try:
    data = request.data
    data = json.loads(data)['data']
    mko_data = data.get("mko")
    inputs = data.get("inputs")
    inputs = encodings.b64decode_datatype(inputs)
    n_samples = int(data.get("n_samples"))

    outputs = sample_inputs_array(mko_data, inputs, n_samples)
    response_text = {
        "outputs": outputs
    }
    return Response(json.dumps(response_text), 200)
  except Exception as err:
    return Response("Sampler error", 409)