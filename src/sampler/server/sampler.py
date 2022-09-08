import pickle
import numpy as np
from common.mko import MKO, encodings
from common.ml import parse_json_model_structure, compile_model

def prepare_mko_model(mko):
  n_inputs = mko.dataspec['n_inputs']
  n_outputs = mko.dataspec['n_outputs']
  model = parse_json_model_structure((n_inputs,), mko._model_name, mko.topology, n_outputs)
  mko._model = compile_model(model, mko.hypers)
  mko._compiled = True
  mko.parameterize_model()
  return mko

def np2d_to_csv(a, precision=8):
  rows = [ ",".join([np.format_float_positional(b,precision=precision, fractional=False) for b in row]) for row in a]
  return "\n".join(rows)

def sample_inputs(mko_data, inputs, n_samples, as_csv=True, precision=8):
  
  if n_samples < 1:
    n_samples = 1
  precision = max(precision, 1)
  mko = MKO.from_base64(mko_data)
  if not mko._has_weights:
    raise Exception("MKO not trained")
  
  inputs = np.array(inputs, dtype=np.float64)
  inputs = mko.normalize_inputs(inputs).repeat(int(n_samples), axis=0)
  
  try:
    mko = prepare_mko_model(mko)
  except Exception as err:
    raise err

  nx = inputs.shape[0]

  try:
    outputs = mko._model.predict(inputs)
    outputs = mko.denormalize_outputs(outputs)
  except Exception as err:
    raise err
  
  if as_csv:
    return np2d_to_csv(outputs, precision)
  else:
    return encodings.b64encode_array(outputs)

