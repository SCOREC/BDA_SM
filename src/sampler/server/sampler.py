import pickle
import numpy as np
from common.mko import MKO, encodings
from common.ml import parse_json_model_structure, compile_model

def prepare_mko_model(mko):
  n_inputs = len(mko.dataspec['inputs'])
  if mko.dataspec["time_as_input"]: n_inputs += 1
  n_outputs = len(mko.dataspec['outputs'])
  model = parse_json_model_structure((n_inputs,), mko._model_name, mko.topology, n_outputs)
  mko._model = compile_model(model, mko.hypers)
  mko._compiled = True
  mko.parameterize_model()
  return mko

def np2d_to_csv(a, precision=8):
  rows = [ ",".join([np.format_float_positional(b,precision=precision, fractional=False) for b in row]) for row in a]
  return "\n".join(rows)

def sample_inputs(mko_data, inputs, n_samples, as_csv=True, precision=8):
  
  n_samples = max(n_samples, 1)
  precision = max(precision, 1)
  mko = MKO.from_base64(mko_data)
  if not mko._has_weights:
    raise Exception("MKO not trained")
  
  try:
    inputs = np.array(inputs, dtype=np.float64).reshape(1,-1)
    inputs = mko.normalize_inputs(inputs).repeat(int(n_samples), axis=0)
  
    mko = prepare_mko_model(mko)
  except Exception as err:
    raise err

  try:
    nx = inputs.shape[0]
    outputs = mko._model.predict(inputs)
    outputs = mko.denormalize_outputs(outputs)
  except Exception as err:
    raise err
  
  if as_csv:
    return np2d_to_csv(outputs, precision)
  else:
    return encodings.b64encode_datatype(outputs)


def sample_inputs_array(mko_data, inputs : np.ndarray, n_samples):
  
  if n_samples < 1:
    n_samples = 1
  mko = MKO.from_base64(mko_data)
  if not mko._has_weights:
    raise Exception("MKO not trained")
  try:
    mko = prepare_mko_model(mko)
  except Exception as err:
    raise err
  
  try:
    (nx, ny) = inputs.shape
    inputs = mko.normalize_inputs(inputs)
    samples = np.empty((nx, len(mko.dataspec['outputs']), n_samples))

    for i in range(n_samples):
      outputs = mko._model.predict(inputs)
      outputs = mko.denormalize_outputs(outputs)
      samples[:,:,i] = outputs
    return encodings.b64encode_datatype(samples)
  except Exception as err:
    raise err

