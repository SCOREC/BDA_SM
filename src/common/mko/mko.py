import json
import mko.encodings

version = 1.0

class MKO(object):
  def __init__(self, model_name: str) -> None:
    self._version = version
    self._model_name = model_name
    self._topological = False
    self._augmented = False
    self._has_hypers = False
    self._has_model = False
    self._compiled = False

    self._topology = { }
    self._hypers = {}
    self._dataspec = {
      "query_json" : {}
    }
    self._model = None

  def _to_dict(self):
    data = {}
    data['model_name'] = self._model_name
    data['topology'] = self._topology
    data['hypers'] = self._hypers
    data['dataspec'] = self._dataspec
    data['model'] = self._model
  
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
    if 'model' in data:
      mko._model = data['model']
      mko._has_model = True

    return mko

  @staticmethod
  def from_json(j_str: str) -> 'MKO':
    data = json.loads(j_str)
    return MKO.from_dict(data)

  @staticmethod
  def from_base64(b64_str: str) -> 'MKO':
    j_str = mko.encodings.decode_base64(b64_str)
    return MKO.from_json(j_str)
    
  ##### SETTERS #####

  def set_compiled(self, state=True):
    self._compiled = state

  ##### GETTERS #####

  def _get_b64(self) -> str:
    j_str = self._get_json()
    return mko.encodings.b64encode(bytes(j_str, "utf-8")).decode("utf-8")
  
  def _get_json(self) -> str:
    return json.dumps(self._to_dict())

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
