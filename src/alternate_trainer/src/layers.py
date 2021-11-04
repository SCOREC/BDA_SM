import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dropout, Dense, Input, Activation
from tensorflow.keras import backend as K
#tf.debugging.set_log_device_placement(True)

supportedKeywords = ['units', 'rate', 'activation']

class VariationalDropout(Dropout):
    def __init__(self, rate, always_drop=True, noise_shape=None, seed=None, **kwargs):
        super(VariationalDropout, self).__init__(rate, noise_shape=noise_shape, seed=seed, **kwargs)
        self.always_drop = always_drop

    def call(self, inputs, always_drop=True):
        if 0.0 < self.rate < 1.0:
            noise_shape = self._get_noise_shape(inputs)

            def dropped_inputs():
                return K.dropout(inputs, 1 - self.rate, noise_shape, seed=self.seed) # NOTE: 1-rate is correct

            if not always_drop:
                return K.in_train_phase(dropped_inputs, inputs, training=self.always_drop)
            return K.in_train_phase(dropped_inputs, inputs, training=True)
        return inputs
