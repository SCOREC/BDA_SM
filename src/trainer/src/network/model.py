import tensorflow as tf
from tensorflow import keras
import network.layers as layers
from tensorflow.keras import backend as K
from mko import MKO

class Model(keras.Sequential):

  def __init__(self, m, **kwargs):
    if m.topological:
      
      seq = [layers.Input(shape=(m.model_structure['nInputs'],),
                          name="Inputs")]

      for ld in m.model_structure['layers']:
        layerargs = {}
        layerfunc = getattr(layers, ld['type'])
        for k, v in ld.items():
          if k in layers.supportedKeywords:
            layerargs[k] = v
        
        seq.append(layerfunc(**layerargs))

      super(Model, self).__init__(seq, **kwargs)