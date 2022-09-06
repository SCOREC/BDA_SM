import json
import common.mko.encodings as encodings

version = 1.0

class MKO(object):
  def __init__(self, model_name: str) -> None:
    self._version = version
    self._model_name = model_name
    self._topological = False
    self._augmented = False
    self._has_hypers = False
    self._has_model = False
    self._has_weights = False
    self._compiled = False
    self._trained = False

    self._topology = { }
    self._hypers = {}
    self._dataspec = {
      "query_json" : {}
    }
    self._model = None
    self._weights = None

  def _to_dict(self):
    data = {}
    data['model_name'] = self._model_name
    data['topology'] = self._topology
    data['hypers'] = self._hypers
    data['dataspec'] = self._dataspec
    
    if self._has_model and self._trained:   
      np_weights = self._model.get_weights()
      b64_encoded_w = []
      for w in np_weights:
        b64_encoded_w.append(encodings.b64encode_array(w))
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
    if self._has_model and self._has_weights:
      self._model.set_weights(
        [ encodings.b64decode_array(w) for w in self._weights ]
      )
    self._trained = True

  @staticmethod
  def from_json(j_str: str) -> 'MKO':
    data = json.loads(j_str)
    return MKO.from_dict(data)

  @staticmethod
  def from_base64(b64_str: str) -> 'MKO':
    j_str = encodings.decode_base64(bytes(b64_str, "utf-8")).decode("utf-8")
    return MKO.from_json(j_str)
    
  ##### SETTERS #####

  def set_compiled(self, state=True):
    self._compiled = state

  ##### GETTERS #####

  def _get_b64(self) -> str:
    j_str = self._get_json()
    return encodings.b64encode(bytes(j_str, "utf-8")).decode("utf-8")
  
  def _get_json(self) -> str:
    as_dict = self._to_dict()
    return json.dumps(as_dict)

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
  def b64(self) -> str:
    return self._get_b64()

  ##### DUNDERS #####
  def __repr__(self) -> str:
    return self.b64

  def __str__(self) -> str:
    return self.b64
