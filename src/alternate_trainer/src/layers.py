import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dropout, Dense, Input, Activation
from tensorflow.keras import backend as K
#tf.debugging.set_log_device_placement(True)

supportedKeywords = ['units', 'rate', 'activation']

class variationalDropout(Dropout):

  def __init__(self, rate, always_drop=True, noise_shape=None, seed=None, **kwargs):
    super(variationalDropout, self).__init__(rate, noise_shape=None, seed=None, **kwargs)
    self.always_drop = always_drop

  def call(self, inputs, always_drop=True):
    if 0.0 < self.rate < 1.0:
      noise_shape = self._get_noise_shape(inputs)

      def dropped_inputs():
        return K.dropout(inputs, self.rate, noise_shape, seed=self.seed)

      if not always_drop:
        return K.in_train_phase(dropped_inputs, inputs, training=self.always_drop)
      return K.in_train_phase(dropped_inputs, inputs, training=always_drop)
    return inputs

custom_objects = {
  "variationalDropout": variationalDropout,
}