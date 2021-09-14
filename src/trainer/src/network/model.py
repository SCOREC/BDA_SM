import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
import network.layers as layers
from tensorflow.keras import backend as K
import os, random, string, base64, tarfile, shutil
from utilities.contexts import in_directory

class Model(keras.Model):

  def __init__(self, m, **kwargs):

    self._mko = m
    super(Model, self).__init__()
    if m.parameterized:

      tmpdir = "/tmp"
      uniquename = m.modelname + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
      basedir = os.path.join(tmpdir, uniquename) 

      try:
        os.mkdir(basedir)
      except:
        raise SystemError("could not create temporary directory")
      
      with in_directory(basedir):
        tarfilename = "model.bz2"
        with open(tarfilename, "wb") as fd:
          fd.write(base64.b64decode(bytes(m.model_saved,'utf-8')))
          fd.close()

        with tarfile.open(tarfilename, "r:bz2") as tar:
          tar.extractall()
          tar.close()

        self = keras.models.load_model("model")
      shutil.rmtree(basedir)
      
    elif m.topological:
      
      super(Model, self).__init__(**kwargs)
      self._layers = []
      # [layers.Input(shape=(m.model_structure['nInputs'],), name="Inputs")]

      for ld in m.model_structure['layers']:
        layer_args = {}
        layer_func = getattr(layers, ld['type'])
        for k, v in ld.items():
          if k in layers.supportedKeywords:
            layer_args[k] = v
        
        self._layers.append(layer_func(**layer_args))

    
  def call(self, input_tensor):

    x = input_tensor
    for layer in self._layers:
      x = layer(x)
    return x

  def get_config(self):
      config = super().get_config()
      config.update({"Model":Model})
      return config

  def compile(self, **kwargs):
    
    tc = self._mko.training_controls
    if 'loss' not in kwargs:
      kwargs['loss'] = keras.losses.MeanSquaredError(reduction='auto')
    if 'optimizer' not in kwargs:
      lr = tc['learning_rate']
      kwargs['optimizer'] = Adam(learning_rate=lr)
    
    super(Model,self).compile(**kwargs)

  def describe(self):
    try:
      print("_is_compiled: {}".format(self._is_compiled))
    except:
      print("_is_compiled not set")
    try:
      print("_is_built: {}".format(self._is_built))
    except:
      print("_is_built not set")

  def train(self, **kwargs):

    (x_train, y_train) = self._mko.training_data
     
    tc = self._mko.training_controls
    if 'batch_size' not in kwargs:
      if 'batch_size' in tc:
        kwargs['batch_size'] = tc['batch_size']
      else:
        kwargs['batch_size'] = 64
      
    if 'epochs' not in kwargs:
      if 'epochs' in tc:
        kwargs['epochs'] = tc['epochs']
      else:
        kwargs['epochs'] = 1

    super(Model, self).fit(x_train, y_train, **kwargs)

  def evaluate(self, **kwargs):

    (x_test, y_test) = self._mko.testing_data
     
    tc = self._mko.training_controls
    if 'batch_size' not in kwargs:
      if 'batch_size' in tc:
        kwargs['batch_size'] = tc['batch_size']
      else:
        kwargs['batch_size'] = 64

    super(Model, self).evaluate(x_test, y_test, **kwargs)

  def save(self, savename, **kwargs):
    with keras.utils.custom_object_scope(layers.custom_objects):
      super(Model, self).save(savename, **kwargs)