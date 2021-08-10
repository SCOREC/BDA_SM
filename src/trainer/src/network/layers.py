import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dropout, Dense, Input, Activation
from tensorflow.keras import backend as K
tf.debugging.set_log_device_placement(True)

supportedKeywords = ['units', 'rate', 'activation']

class variationalDropout(Dropout):

  def __init__(self, rate, training=None, noise_shape=None, seed=None, **kwargs):
    super(variationalDropout, self).__init__(rate, noise_shape=None, seed=None, **kwargs)
    self.training = training

  def call(self, inputs, training=None):
    if 0.0 < self.rate < 1.0:
      noise_shape = self._get_noise_shape(inputs)

      def dropped_inputs():
        return K.dropout(inputs, self.rate, noise_shape, seed=self.seed)

      if not training:
        return K.in_train_phase(dropped_inputs, inputs, training=self.training)
      return K.in_train_phase(dropped_inputs, inputs, training=training)
    return inputs

"""
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
x_train = x_train.astype("float32")/ 255.0
x_test = x_test.astype("float32")/ 255.0

model = keras.Sequential(
  [
    keras.Input(shape=(32, 32, 3)),
    layers.Conv2D(32, (3, 3), padding='valid', activation='relu'),
    layers.MaxPool2D(pool_size=(2, 2)),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPool2D(),
    Dropout(0.1, training=True),
    layers.Conv2D(128, 3, activation='relu'),
    layers.Flatten(),
    Dropout(0.1, training=True),
    layers.Dense(64, activation='relu'),
    Dropout(0.1, training=True),
    layers.Dense(10),
    layers.Dense(64, activation='relu'),
    Dropout(0.1, training=True),
    layers.Dense(10),
    layers.Dense(64, activation='relu'),
    Dropout(0.1, training=True),
    layers.Dense(10),
  ]
)

model.compile(
  loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
  optimizer=keras.optimizers.Adam(lr=3.0e-4),
  metrics=['accuracy'],
)

model.fit(x_train, y_train, batch_size=64, epochs=1, verbose=2)
model.evaluate(x_test, y_test, batch_size=64, verbose=2)

model.save("nn.h5")

json_string = model.to_json(indent=1)
print(json_string)
"""