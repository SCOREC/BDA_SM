import json
import numpy as np
import common.utilities.encodings as encodings

version = 1.0

class MKO(object):
  def __init__(self, model_name: str) -> None:
    self._version = version
    self._model_name = model_name
    self._topological = False
    self._augmented = False
    self._has_hypers = False
    self._compiled = False
    self._has_weights = False
    self._parameterized = False

    self._topology = { }
    self._hypers = {}
    self._dataspec = {
      "query_json" : {}
    }
    self._model = None
    self._weights = None
    self._history = None

  def _to_dict(self):
    data = {}
    data['model_name'] = self._model_name
    data['topology'] = self._topology
    data['hypers'] = self._hypers
    data['dataspec'] = self._dataspec
    
    if self._has_weights and self._compiled:   
      np_weights = self._model.get_weights()
      b64_encoded_w = []
      for w in np_weights:
        b64_encoded_w.append(encodings.b64encode_datatype(w))
      data['WEIGHTS'] = b64_encoded_w
    return data
  
  @staticmethod
  def from_dict(data: dict) -> 'MKO':
    mko = MKO(data['model_name'])
    if 'topology' in data:
      mko._topology = data['topology']
      mko._topological = True
    if 'hypers' in data:
      mko._hypers = data['hypers']
      mko._has_hypers = True
    if 'dataspec' in data:
      mko._dataspec = data['dataspec']
      mko._augmented = True
    if 'WEIGHTS' in data:
      mko._has_weights = True
      mko._weights = data['WEIGHTS']
    return mko

  def parameterize_model(self):
    if self._compiled and self._has_weights:
      self._model.set_weights(
        [ encodings.b64decode_datatype(w) for w in self._weights ]
      )
      self._parameterized = True

  @staticmethod
  def from_json(j_str: str) -> 'MKO':
    data = json.loads(j_str)
    return MKO.from_dict(data)

  @staticmethod
  def from_base64(b64_str: str) -> 'MKO':
    j_str = encodings.decode_base64(b64_str).decode("utf-8")
    return MKO.from_json(j_str)

  @staticmethod
  def scale_array(array, interval):
    means = interval.mean(axis=0)
    tmp = np.empty_like(array)
    for i in range(array.shape[1]):
      tmp[:,i] = (array[:,i] - means[i]) / (interval[1,i] - interval[0,i])
    return array

  @staticmethod
  def unscale_array(array, interval):
    means = interval.mean(axis=0)
    tmp = np.empty_like(array)
    for i in range(array.shape[1]):
      tmp[:,i] = array[:,i] * (interval[1,i] - interval[0,i]) + means[i]
    return array

  @classmethod
  def normalize(cls, array):
    tmp = np.array(array)
    means = tmp.mean(axis=0)
    std = tmp.std(axis=0)
    ll = means - std
    ul = means + std
    interval = np.array([ll, ul])
    normalized_array = cls.scale_array(tmp, interval)
    return normalized_array, interval

  @classmethod
  def denormalize(cls, array, interval):
    return cls.unscale_array(array, interval)
  
  def normalize_training_inputs(self, array):
    scaled_array, interval = self.normalize(array)
    self.set_inputs_interval(interval)
    return scaled_array

  def normalize_training_outputs(self, array):
    scaled_array, interval = self.normalize(array)
    self.set_outputs_interval(interval)
    return scaled_array
    
  def normalize_inputs(self, array):
    interval = self.get_inputs_interval()
    return self.scale_array(array, interval)

  def denormalize_inputs(self, array):
    interval = self.get_inputs_interval()
    return self.denormalize(array, interval)

  def denormalize_outputs(self, array):
    interval = self.get_outputs_interval()
    return self.denormalize(array, interval)

  ##### SETTERS #####

  def set_compiled(self, state=True):
    self._compiled = state

  def set_trained(self, state=True):
    self._has_weights = state

  def set_inputs_interval(self, interval):
    self._dataspec['inputs_interval'] = encodings.b64encode_datatype(interval)

  def set_outputs_interval(self, interval):
    self._dataspec['outputs_interval'] = encodings.b64encode_datatype(interval)

  def add_loss_history(self, history):
    if not self.has_hypers:
      return
    if "loss_history" not in self._hypers:
      self._hypers["loss_history"] = []
    self._hypers["loss_history"] = self._hypers["loss_history"] + history

  def add_lr_history(self, history):
    if not self.has_hypers:
      return
    if "lr_history" not in self._hypers:
      self._hypers["lr_history"] = []
    self._hypers["lr_history"] = self._hypers["lr_history"] + history


  ##### GETTERS #####

  def _get_b64(self) -> str:
    j_str = self._get_json()
    return encodings.encode_base64(j_str)
  
  def _get_json(self) -> str:
    as_dict = self._to_dict()
    return json.dumps(as_dict)

  def get_inputs_interval(self):
    return encodings.b64decode_datatype(self._dataspec['inputs_interval'])

  def get_outputs_interval(self):
    return encodings.b64decode_datatype(self._dataspec['outputs_interval'])

  ##### PROPERTIES #####
  @property
  def topological(self):
    return self._topological

  @property
  def has_hypers(self):
    return self._has_hypers

  @property
  def hypers(self):
    return self._hypers
  
  @property
  def augmented(self):
    return self._augmented
  
  @property
  def dataspec(self):
    return self._dataspec

  @property
  def topology(self):
    return self._topology

  @property
  def has_weights(self):
    return self._has_weights

  @property
  def parameterized(self):
    return self._parameterized

  @property
  def trainable(self) -> bool:
    return (
      self._topological and
      self._has_hypers  and
      self._augmented
    )
  
  @property
  def compiled(self) -> bool:
    return self._compiled

  @property
  def series_type(self):
    return self.dataspec["series_type"].lower()

  @property
  def b64(self) -> str:
    return self._get_b64()

  ##### DUNDERS #####
  def __repr__(self) -> str:
    return self.b64

  def __str__(self) -> str:
    return self.b64
