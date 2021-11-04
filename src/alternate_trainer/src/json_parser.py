import tensorflow as tf
from tensorflow import keras
from keras import Input, Model
from keras.layers import Dense, Conv2D
from src.layers import variationalDropout

class Defaults:
    rate = 0.95
    activation = "relu"
    padding = "valid"
    stride = 1

class LayerKeys:
    TYPE = "type"
    UNITS = "units"
    ACTIVATION = "activation"
    INITIALIZER = "kernel_initializer"
    NAME = "name"
    RATE = "rate"
    FILTERS = "filters"
    KERNEL_SIZE = "kernel_size"
    STRIDE = "stride"
    PADDING = "padding"

def verify_activation(activation_function): # TODO: implement
    return True

def get_dense(layer_params, name): # TODO: write descriptive error names (make exception class)
    # TODO: clean up validation, should be able to be more modularized
    if LayerKeys.UNITS not in layer_params:
        raise Exception()

    try:
        units = int(layer_params[LayerKeys.UNITS])
    except ValueError:
        raise Exception()

    if LayerKeys.ACTIVATION not in layer_params:
        activation = Defaults.activation
    else:
        activation = layer_params[LayerKeys.ACTIVATION].lower()

    if not verify_activation(activation):
        raise Exception()

    if LayerKeys.INITIALIZER not in layer_params:
        if activation == "relu" or activation == "leakyrelu":
            initializer = "he_uniform"
        else:
            initializer = "golorot_uniform"
    else:
        initializer = layer_params[LayerKeys.INITIALIZER]

    return Dense(units, activation=activation, kernel_initializer=initializer, name=name)


def dropout(layer_params, name):
    if LayerKeys.RATE not in layer_params:
        rate = Defaults.rate
    else:
        rate = layer_params[LayerKeys.RATE]

    return variationalDropout(rate, name=name)

def get_convolutional(layer_params, name):
    if LayerKeys.FILTERS not in layer_params:
        raise Exception()

    filters = layer_params[LayerKeys.FILTERS]

    if LayerKeys.KERNEL_SIZE not in layer_params:
        raise Exception()

    kernel_size = layer_params[LayerKeys.KERNEL_SIZE]

    if LayerKeys.STRIDE not in layer_params:
        stride = Defaults.stride
    else:
        stride = layer_params[LayerKeys.STRIDE]

    if LayerKeys.PADDING not in layer_params:
        padding = Defaults.padding
    else:
        padding = layer_params[LayerKeys.PADDING]

    return Conv2D(filters, kernel_size, stride, padding, name=name)


layers = {
    "dense": get_dense,
    "dropout": dropout,
    "variational_dropout": dropout,
    "convolutional": get_convolutional,
}

def get_layer(layer_params, index):
    if LayerKeys.NAME in layer_params:
        name = layer_params[LayerKeys.NAME]
    else:
        name = "layer_{:02d}".format(index)

    if LayerKeys.TYPE not in layer_params:
        print(layer_params, str(LayerKeys.TYPE))
        raise KeyError("'{}' not in layer '{}'".format(LayerKeys.TYPE, name))

    layer_type = layer_params[LayerKeys.TYPE].lower()

    if layer_type not in layers:
        raise Exception()

    return layers[layer_type](layer_params, name)

def parse_json_model_structure(data_input_shape: tuple, name: str, inputs: list) -> Model:
    inpt = Input(data_input_shape)
    x = inpt
    for index, layer_params in enumerate(inputs):
        layer_type = get_layer(layer_params, index)
        x = layer_type(x)

    return Model(inputs=inpt, outputs=x, name=name)
