import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.layers import Dropout, Dense, Lambda, InputSpec, Wrapper
from tensorflow.keras import backend as K
from tensorflow.keras import initializers

class ConcreteDropout(Wrapper):
  def __init__( self, layer, weight_regularizer=1e-6, dropout_regularizer=1e-5, ** kwargs):
    assert('kernel_regularizer' not in kwargs)
    super(ConcreteDropout, self).__init__(layer, **kwargs)
    self.weight_regularizer = K.cast_to_floatx(weight_regularizer)
    self.dropout_regularizer = K.cast_to_floatx (dropout_regularizer)
    self.supports_masking = True
  def build(self, input_shape=None) :
    self.input_spec = InputSpec(shape=input_shape)
    if not self.layer.built:
      self.layer.build(input_shape)
      self.layer.built = True

    super(ConcreteDropout, self).build()
    # initialise p
    self.p_logit = self.add_weight(shape=(1,), initializer=initializers.RandomUniform(-2., 0.), name='p_logit', trainable=True)
    self.p = K.sigmoid(self.p_logit[0])
    # initialise regulariser / prior KL term
    input_dim = input_shape[-1] # we drop only last dim
    weight=self.layer.weights[0]
    # Note : we divide by (1 - p) because we scaled layer output by (1 - p)
    kernel_regularizer = self.weight_regularizer * K.sum(K.square(weight)) / (1.-self.p)
    dropout_regularizer = self.p * K.log(self.p)
    dropout_regularizer += (1.-self.p) * K.log(1.-self.p)
    dropout_regularizer *= self.dropout_regularizer * input_dim
    regularizer = K.sum(kernel_regularizer + dropout_regularizer)
    self.add_loss (regularizer)

  def compute_output_shape(self, input_shape):
    return self.layer.compute_output_shape(input_shape)

  def concrete_dropout(self, x):
    eps = K.cast_to_floatx(K.epsilon())
    temp = 1.0 / 10.0
    unif_noise = K.random_uniform(shape=K.shape(x))
    drop_prob = (
        K.log(self.p+eps) - K.log(1.-self.p+eps) + K.log(unif_noise+eps) - K.log(1.-unif_noise+eps)
      )
    drop_prob = K.sigmoid(drop_prob / temp)
    random_tensor = 1. - drop_prob
    retain_prob = 1. - self.p
    x *= random_tensor
    x /= retain_prob
    return x

  def call ( self , inputs , training = None ) :
    return self.layer.call(self.concrete_dropout(inputs))


class VariationalDropout(Dropout):
    def __init__(self, rate, always_drop=True, noise_shape=None, seed=None, **kwargs):
        super(VariationalDropout, self).__init__(rate, noise_shape=noise_shape, seed=seed, **kwargs)
        self.always_drop = always_drop
        self.variational = True

    def call(self, inputs, always_drop=True):
        if 0.0 < self.rate < 1.0:
            noise_shape = self._get_noise_shape(inputs)

            def dropped_inputs():
                return K.dropout(inputs, 1 - self.rate, noise_shape, seed=self.seed) # NOTE: 1-rate is correct

            if not always_drop:
                return K.in_train_phase(dropped_inputs, inputs, training=self.always_drop)
            return K.in_train_phase(dropped_inputs, inputs, training=True)
        return inputs
