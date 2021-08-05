import sys
import json
import datetime

class MKO(object):
  """The information necessary to instantiate a NN"""
  
  def __init__(self, js=None):

    try:
      data = json.loads(js)
    except Exception as err:
      print("invalid json string provided")
      return

    self.modelname = data["modelname"]

    try:
      self.Model_structure = data["Model_structure"]
      json.dumps(self.Model_structure)
      self._topographic = True
    except:
      self._topographic = False

    try:
      self.modelSaved = data['modelSaved']
      self._parameterized = True
    except:
      self._parameterized = False

    try:
      self.setDataDescriptor(data['data_descriptor'])
    except Exception as err:
      raise err

    if 'training_controls'  in data:
      if 'new_iterations' in data['training_controls']:
        self.new_iterations = data['training_controls']['new_iterations']
      if 'learning_rate' in data['training_controls']:
        self.learning_rate = data['training_controls']['learning_rate']
      
    return

  def topographic(self):
    return self._topographic
  
  def augmented(self):
    return self._augmented
  
  def parameterized(self):
    return self._parameterized
  
  def setTopology(self, s):
    try:
      self.Model_structure = json.loads(s)
      self._topographic = True
    except:
      self._topographic = False

  def setParameters(self, s):
    try:
      self.modelSaved = s
      self._parameterized = True
    except:
      self._parameterized = False

  def setDataDescriptor(self, data):
    try:
      self.serverName = data['serverName']
      self.serverJWT = data['serverJWT']
      self.tag_ids = data['tag_ids']
      self.attr_ids = data['attr_ids']
      self.start_time = datetime.datetime.min
      self.end_time = datetime.datetime.max
      self.offset = 0
      self.max_samples = sys.maxint

      self._augmented = True
      if 'start_time' in data:
        self.start_time = data['start_time']
      if 'end_time' in data:
        self.end_time = data['end_time']
      if 'offset' in data:
        self.offset = data['offset']
      if 'max_samples' in data:
        self.max_samples = data['max_samples']
    except Exception as e:
      self._augmented = False
      raise(e)