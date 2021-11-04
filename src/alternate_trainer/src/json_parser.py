from keras.regularizers import get
import tensorflow as tf
from tensorflow import keras
from keras import Input, Model
from keras.layers import Dense, Conv2D
from src.layers import VariationalDropout
from src.exceptions import InputException, InvalidArgument

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

def check_in(field: str, layer_params: dict) -> bool:
    return field in layer_params

def enforce(field: str, layer_params: dict):
    if check_in(field, layer_params):
        raise InputException(LayerKeys.UNITS)

    return layer_params[field]

def get_value(field: str, default: any, layer_params: dict) -> any:
    if check_in(field, layer_params):
        return layer_params[field]
    return default

def get_dense(layer_params: dict, name: str):
    units = enforce(LayerKeys.UNITS)

    if type(units) != int:
        raise InputException(LayerKeys.UNITS, ('int', type(units)))

    activation = get_value(LayerKeys.ACTIVATION, Defaults.activation, layer_params).lower()

    if activation == "relu" or activation == "leakyrelu":
        default = "he_uniform"
    else:
        default = "glorot_uniform"

    initializer = get_value(LayerKeys.INITIALIZER, default, layer_params)

    return Dense(units, activation=activation, kernel_initializer=initializer, name=name)

def dropout(layer_params, name):
    if LayerKeys.RATE not in layer_params:
        rate = Defaults.rate
    else:
        rate = layer_params[LayerKeys.RATE]

    return VariationalDropout(rate, name=name)

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
    name = get_value(LayerKeys.NAME, "layer_{:02d}".format(index), layer_params)
    layer_type = enforce(LayerKeys.TYPE, layer_params).lower()

    if layer_type not in layers:
        raise InvalidArgument(layer_type, layers)

    return layers[layer_type](layer_params, name)

def parse_json_model_structure(data_input_shape: tuple, name: str, model_topology: list) -> Model:
    input_layer = Input(data_input_shape)
    x = input_layer
    for index, layer_params in enumerate(model_topology):
        layer_type = get_layer(layer_params, index)
        x = layer_type(x)

    return Model(inputs=input_layer, outputs=x, name=name)
