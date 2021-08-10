
class MKO(object):

  def __init__(self, c):
    

    try:
      self.modelname = c['modelname']
    except:
      raise AttributeError("No modelname for MKO")
    
    if "modelSaved" in c and c["modelSaved"] is not None:
      self.modelSaved = c["modelSaved"]

    if "network" in c:
      self.model_structure = c['network']
      self._topological = True
    else:
      self._topological = False
    
    if "data_descriptor" in c and c["data_descriptor"] is not None:
      self.data_descriptor = c['data_descriptor']
      self._augmented = True
    else:
      self._augmented = False
    
    if "trainingData" in c and c["trainingData"] is not None:
      self.trainingData = c['trainingData']

  @property
  def topological(self):
    return self._topological

  @property
  def augmented(self):
    return self._augmented
