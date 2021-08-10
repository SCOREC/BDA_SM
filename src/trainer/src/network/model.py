import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras.optimizer_v2.adam import Adam
import network.layers as layers
from tensorflow.keras import backend as K

class Model(keras.Sequential):

  def __init__(self, m, **kwargs):
    if m.topological:
      
      seq = [layers.Input(shape=(m.model_structure['nInputs'],),
                          name="Inputs")]

      for ld in m.model_structure['layers']:
        layer_args = {}
        layer_func = getattr(layers, ld['type'])
        for k, v in ld.items():
          if k in layers.supportedKeywords:
            layer_args[k] = v
        
        seq.append(layer_func(**layer_args))

      super(Model, self).__init__(seq, **kwargs)

      self._mko = m
    
  def compile(self, **kwargs):
    
    tc = self._mko.training_controls
    if 'loss' not in kwargs:
      kwargs['loss'] = keras.losses.MeanSquaredError(reduction='auto')
    if 'optimizer' not in kwargs:
      lr = tc['learning_rate']
      kwargs['optimizer'] = Adam(lr=lr)
    
    super(Model,self).compile(**kwargs)

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
