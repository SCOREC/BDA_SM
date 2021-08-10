import os
import numpy as np
import pandas as pd
import random, string, base64, json
from pandas.core.base import DataError
from errors import MKOError
import tarfile

class MKO(object):

  def __init__(self, c):
    
    try:
      self.modelname = c['modelname']
    except:
      raise AttributeError("No modelname for MKO")
    
    if "model_saved" in c and c["model_saved"] is not None:
      self.model_saved = c["model_saved"]

    if "model_structure" in c:
      self.model_structure = c['model_structure']
      self._topological = True
    else:
      self._topological = False
    
    if "data_descriptor" in c and c["data_descriptor"] is not None:
      self._data_descriptor = c['data_descriptor']
      self._augmented = True
    else:
      self._data_descriptor = None
      self._augmented = False
    
    if "training_controls" in c and c["training_controls"] is not None:
      self.training_controls = c['training_controls']

    self._data_populated = False

  @classmethod
  def from_Model(cls, model):

    savedir = "/tmp"
    m = model._mko
    savename = m.modelname + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    abssavename =os.path.join(savedir, savename) 
    model.save(abssavename)
    tarfilename = abssavename + ".bz2"
    with tarfile.open(tarfilename, "w:bz2") as tar:
      tar.add(abssavename, recursive=True)
      tar.close()

    with open(tarfilename, "rb") as fd:
      model_saved = fd.read()
      fd.close()


    m.set_parameters(str(base64.b64encode(model_saved)))
    print("type of params: {}".format(type(m.model_saved)))

    return m


  def set_parameters(self, param):
    self._parameterized = True
    self.model_saved = param

  @property
  def topological(self):
    return self._topological

  @property
  def augmented(self):
    return self._augmented

  @property
  def data_descriptor(self):
    if not self.augmented:
      return None
    return self._data_descriptor
  
  @property
  def training_data(self):
    if not self.augmented:
      raise MKOError("Cannot get data from unaugmented MKO")

    if not self._data_populated:
      try:
        self.fetch_data()
      except Exception as err:
        raise MKOError("Could not get training data")
    return (np.array(self.x_train), np.array(self.y_train))
    
  @property
  def testing_data(self):
    if not self.augmented:
      raise MKOError("Cannot get data from unaugmented MKO")

    if not self._data_populated:
      try:
        self.fetch_data()
      except Exception as err:
        raise MKOError("Could not get testing data")
    return (np.array(self.x_test), np.array(self.y_test))

  @property
  def validation_data(self):
    if not self.augmented:
      raise MKOError("Cannot get data from unaugmented MKO")

    if not self._data_populated:
      try:
        self.fetch_data()
      except DataError as err:
        raise MKOError("Could not get validation data")
    return (np.array(self.x_val), np.array(self.y_val))
  
  def fetch_data(self):
    if not self.augmented:
      raise MKOError

    d = self.data_descriptor
    tc = self.training_controls

    if d['type'] == 'http':
      try:
        df = pd.read_csv(d['URL'], header=None)
      except:
        raise DataError("data not accessible at {}".format(d.get('URL')))

    else:
      raise DataError("descriptor type {} not implemented".format(d['type']))

    nrows, ncols = df.shape
    ic = d['input_features']
    oc = d['output_features']
    assert(ic + oc == ncols)
    
    r1 = int(tc['training_set_fraction'] * nrows)
    r2 = r1 + int(tc['testing_set_fraction'] * nrows)

    a = np.array(df)
    self.x_train = a[:r1, :ic].tolist()
    self.y_train = a[:r1, ic:ic+oc].tolist()

    self.x_test = a[r1:r2, :ic].tolist()
    self.y_test = a[r1:r2, ic:ic+oc].tolist()

    if r2 == nrows:
      x_val = None
      y_val = None
    else:
      self.x_val = a[r2:, :ic].tolist()
      self.y_val = a[r2:, ic:ic+oc].tolist()

    self._data_populated = True

  def save(self, c, filename=None):
    try:
      savefile = c['savefile']
    except:
      savefile = filename

    with open(savefile, "w") as fd:
      json.dump(vars(self), fd)
