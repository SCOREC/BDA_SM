from src.json_parser import parse_json_model_structure
import json
from typing import Optional
import pickle
import numpy as np
import base64
import tensorflow as tf
from tensorflow.keras import backend as K

# temporary placeholder
version = "1.0"

class MKO:
    class Fields:
        EPOCHS = "epochs"
        BATCH_SIZE = "batch_size"
        DATA_SHAPE = "data_shape"
        MODEL_NAME = "model_name"
        TOPOLOGY = "topology"
        VERSION = "version"
        OPTIMIZER = "optimizer"
        # HYPER_PARAMS = "hyper_params" # add support for momentum?
        LEARNING_RATE = "learning_rate"
        LOSS_FUNCTION = "loss_function"
        DATA_PATH = "data_path"

        MANDATORY_FIELDS = {
            EPOCHS,
            BATCH_SIZE,
            DATA_SHAPE,
            MODEL_NAME,
            TOPOLOGY,
            VERSION,
            OPTIMIZER,
            # HYPER_PARAMS,
            LOSS_FUNCTION,
            DATA_PATH
        }

        LIST_FIELDS = {
            TOPOLOGY
        }

    class InputException(Exception):
        def __init__(self, field: str, type_error: Optional[tuple] = None):
            if type_error == None:
                super().__init__("field '{}' not in input json".format(field))
            else:
                super().__init__("field '{}' not of type '{}' instead is type '{}'".format(field, type_error[0], type_error[1]))

    class VersionException(Exception):
        def __input__(self, source_version: str, json_version: str):
            super().__init__("source version {} != json version {}".format(source_version, json_version))

    def __init__(self, params: dict):
        self.parse_params(params)
        self._model = parse_json_model_structure(self._data_shape, self._model_name, self._topology)
        self._trained = False
        self._compiled = False
        self._loss = None
        self._data_loaded = False

    @staticmethod
    def from_MKO(mko: str):
        # TODO: Implement
        pass

    @staticmethod
    def enforce(field: str, input_params: dict):
        if field not in input_params:
            raise MKO.InputException(field)

        if field in MKO.Fields.LIST_FIELDS and type(input_params[field]) != list:
            raise MKO.InputException(field, ("dict", type(input_params[field])))
    

    def parse_params(self, input_params: dict):
        for field in MKO.Fields.MANDATORY_FIELDS:
            MKO.enforce(field, input_params)
            setattr(self, "_{}".format(field), input_params[field])

        if version != self._version:
            raise MKO.VersionException(version, self._version)

    def compile(self):
        self._model.compile(loss=self._loss_function, optimizer=self._optimizer)
        K.set_value(self._model.optimizer.learning_rate, self._learning_rate)
        self._compiled = True

    def load_data(self): # TODO: implement
        self._data_loaded = True

    def train(self):
        if not self._data_loaded:
            raise Exception("data not loaded, call 'load_data' before 'train'")

        if not self._compiled:
            raise Exception("model not compiled, call 'compile' before train")

        if type(self._epochs) != int: # change to automattically enforce in Fields
            raise MKO.InputException(MKO.Fields.EPOCHS, ("int", type(self._epochs)))

        if type(self._batch_size) != int:
            raise MKO.InputException(MKO.Fields.BATCH_SIZE, ("int", type(self._batch_size)))

        self._model.fit(self._X_train, self._Y_train, epochs=self._epochs, batch_size=self._batch_size)
        self._loss = self._model.evaluate(self._X_test, self._Y_test)

    def make_inference(self, x, samples) -> tf.Tensor:
        X = tf.transpose(tf.reshape(tf.repeat(x, repeats=samples), (len(x), samples)))
        return self._model.predict(X)

    @staticmethod
    def b64decode_array(string: str) -> np.array:
        return pickle.loads(base64.b64decode(string))

    @staticmethod
    def b64encode_array(array: np.array) -> str:
        return base64.b64encode(pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)).decode('ascii')

    def get_dict(self) -> dict:
        to_save = {}
        for field in MKO.Fields.MANDATORY_FIELDS:
            to_save[field] = getattr(self, "_{}".format(field))

        to_save["trained"] = self._trained
        to_save["loss"] = self._loss
        np_weights = self._model.get_weights()
        b64_encoded_w = []
        for w in np_weights:
            b64_encoded_w.append(MKO.b64encode_array(w))

        to_save["weights"] = b64_encoded_w

        return to_save
    
    def get_json(self) -> str:
        return json.dumps(self.get_dict())
    
    def __str__(self) -> str:
        return self.get_json()
        
    def __repr__(self) -> str:
        return self.get_json()

        