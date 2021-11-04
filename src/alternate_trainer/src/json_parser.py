from os import stat
from typing import Any
from keras import Input, Model
from keras.layers import Dense, Conv2D
from src.layers import VariationalDropout
from src.exceptions import InputException, InvalidArgument

class Defaults:
    rate = 0.95
    activation = "relu"
    padding = "valid"
    stride = 1

    @staticmethod
    def get_default_initializer(activation: str) -> str:
        if activation == "relu" or activation == "leakyrelu":
            return "he_uniform"
        return "glorot_uniform"

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
    if not check_in(field, layer_params):
        raise InputException(field)

    return layer_params[field]

def get_value(field: str, default: Any, layer_params: dict) -> Any:
    if check_in(field, layer_params):
        return layer_params[field]

    return default

def get_dense(layer_params: dict, name: str):
    units = enforce(LayerKeys.UNITS, layer_params)
    activation = get_value(LayerKeys.ACTIVATION, Defaults.activation, layer_params).lower()
    initializer = get_value(LayerKeys.INITIALIZER, Defaults.get_default_initializer(activation), layer_params)
    return Dense(units, activation=activation, kernel_initializer=initializer, name=name)

def dropout(layer_params: dict, name: str):
    rate = get_value(LayerKeys.RATE, Defaults.rate, layer_params)
    return VariationalDropout(rate, name=name)

def get_convolutional(layer_params: dict, name: str):
    filters = enforce(LayerKeys.FILTERS, layer_params)
    kernel_size = enforce(LayerKeys.KERNEL_SIZE, layer_params)
    stride = get_value(LayerKeys.STRIDE, Defaults.stride, layer_params)
    padding = get_value(LayerKeys.PADDING, Defaults.padding, layer_params)
    
    return Conv2D(filters, kernel_size, stride, padding, name=name)


layers = {
    "dense": get_dense,
    "dropout": dropout,
    "variational_dropout": dropout,
    "convolutional": get_convolutional,
}

def get_layer(layer_params: dict, index: int):
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
