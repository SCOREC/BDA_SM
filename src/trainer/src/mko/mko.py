import os
import numpy as np
import pandas as pd
import random, string, base64, json, shutil, tarfile
from pandas.core.base import DataError

from ..errors import MKOError
from ..utilities.contexts import in_directory

class MKO():

  def __init__(self, c=None, dict=None):
    
    if dict is not None:
      self.__dict__ = dict
      return 

    try:
      self.modelname = c['modelname']
    except:
      raise AttributeError("No modelname for MKO")
    
    if "model_saved" in c and c["model_saved"] is not None:
      self.model_saved = c["model_saved"]
      self._parameterized = True
    else:
      self._parameterized = False

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

    m = model._mko

    tmpdir = "/tmp"
    uniquename = m.modelname + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    basedir = os.path.join(tmpdir, uniquename) 

    try:
      os.mkdir(basedir)
    except:
      raise SystemError("could not create temporary directory")
    
    with in_directory(basedir):
      model_save_name = os.path.join(basedir, "model")
      model.save(model_save_name)

      tarfilename = "model.bz2"
      with tarfile.open(tarfilename, "w:bz2") as tar:
        tar.add("model", recursive=True)
        tar.close()

      with open("model.bz2", "rb") as fd:
        model_saved = fd.read()
        fd.close()
      
    shutil.rmtree(basedir)

    m.set_parameters(base64.b64encode(model_saved).decode('utf-8'))
    print("type of params: {}".format(type(m.model_saved)))

    return m


  def set_parameters(self, param):
    self._parameterized = True
    self.model_saved = param

  @property
  def parameterized(self):
    return self._parameterized

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

  @classmethod
  def load(cls, filename):

    with open(filename, "r") as fd:
      data = json.load(fd)
      return MKO(dict=data)

  def save(self, c, filename=None):
    try:
      savefile = c['savefile']
    except:
      savefile = filename

    with open(savefile, "w") as fd:
      json.dump(vars(self), fd)
