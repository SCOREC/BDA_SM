from re import S
from src.json_parser import parse_json_model_structure
import json
import pickle
import numpy as np
import base64
import tensorflow as tf
from tensorflow.keras import backend as K
import pandas as pd
from src.exceptions import InputException, VersionException
from src.MKO_fields import Fields

# temporary placeholder
version = "1.0"

class MKO:
    def __init__(self, params: dict):
        self._trained = 0
        self._data_loaded = False
        self._compiled = False
        self._loss = None
        self.parse_params(params)

    @staticmethod
    def from_json(json_text: str):
        return MKO(json.loads(json_text))

    @staticmethod
    def from_empty(name: str):
        empty = {
            Fields.MODEL_NAME: name,
            Fields.VERSION: version
        }
        return MKO(empty)

    @staticmethod
    def enforce(field: str, input_params: dict):
        if field not in input_params:
            raise InputException(field)

        if field in Fields.LIST_FIELDS and type(input_params[field]) != list:
            raise InputException(field, ("list", type(input_params[field])))

        if field in Fields.DICT_FIELDS and type(input_params[field]) != dict:
            raise InputException(field, ("dict", type(input_params[field])))

    @property
    def topographic(self):
        return self._topology != None

    @property
    def augmented(self):
        return self._data

    def parse_fields(self, fields: set, input_params: dict):
        for field in fields:
            MKO.enforce(field, input_params)
            setattr(self, "_{}".format(field), input_params[field])

    def parse_params(self, input_params: dict):
        self.parse_fields(Fields.MANDATORY_FIELDS, input_params)

        for field_enum in Fields.OPTIONAL_SUB_FIELDS:
            if field_enum in input_params:
                setattr(self, "_{}".format(field_enum), True)
                self.parse_fields(Fields.OPTIONAL_SUB_FIELDS[field_enum].MANDATORY_FIELDS, input_params[field_enum])
            else:
                setattr(self, "_{}".format(field_enum), False)

        for field in Fields.OPTIONAL_FIELDS:
            if field in input_params:
                setattr(self, "_{}".format(field), input_params[field])

        if Fields.TOPOLOGY in input_params:
            MKO.enforce(Fields.TOPOLOGY, input_params)
            self._topology = input_params[Fields.TOPOLOGY]
            # assert data_shape and topology exists
            self._model = parse_json_model_structure(self._data_shape, self._model_name, self._topology)
        else:
            self.topology = None

        if Fields.WEIGHTS in input_params:
            MKO.enforce(Fields.WEIGHTS, input_params)
            self._model.set_weights([MKO.b64decode_array(w) for w in input_params[Fields.WEIGHTS]])


        if version != self._version:
            raise VersionException(version, self._version)

    def compile(self):
        # assert topological
        self._model.compile(loss=self._loss_function, optimizer=self._optimizer)
        K.set_value(self._model.optimizer.learning_rate, self._learning_rate)
        self._compiled = True

    def load_data(self): # TODO: implement data_descripter instead of path
        # assert augmented
        with open(self._data_path.format("x"), "r") as file:
            x = pd.read_csv(file).to_numpy()
        with open(self._data_path.format("y"), "r") as file:
            y = pd.read_csv(file).to_numpy()

        if type(self._train_percent) != float:
            raise InputException(Fields.TRAIN_PERCENT, ('float', type(self._train_percent)))
        index = int(self._train_percent * len(x))
        permutation = np.random.permutation(len(x))
        x = x[permutation]
        y = y[permutation]
        self._X_train = x[0:index]
        self._X_test = x[index:]
        self._Y_train = y[0:index]
        self._Y_test = y[index:]
        self._data_loaded = True

    def train(self):
        # assert augmented + topological
        if not self._data_loaded:
            raise Exception("data not loaded, call 'load_data' before 'train'")

        if not self._compiled:
            raise Exception("model not compiled, call 'compile' before train")

        if type(self._epochs) != int: # change to automattically enforce in Fields
            raise InputException(Fields.EPOCHS, ("int", type(self._epochs)))

        if type(self._batch_size) != int:
            raise InputException(Fields.BATCH_SIZE, ("int", type(self._batch_size)))

        self._model.fit(self._X_train, self._Y_train, epochs=self._epochs, batch_size=self._batch_size)
        self._loss = self._model.evaluate(self._X_test, self._Y_test)
        self._trained += self._epochs

    def make_inference(self, x, samples) -> tf.Tensor:
        # assert topological
        X = tf.transpose(tf.reshape(tf.repeat(x, repeats=samples), (len(x), samples)))
        return self._model.predict(X)
        
    @staticmethod
    def b64decode_array(string: str) -> np.array:
        return pickle.loads(base64.b64decode(string))

    @staticmethod
    def b64encode_array(array: np.array) -> str:
        return base64.b64encode(pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)).decode('ascii')

    def save_fields(self, fields: set, to_save: dict):
        for field in fields:
            to_save[field] = getattr(self, "_{}".format(field))

    def get_dict(self) -> dict:
        to_save = {}
        self.save_fields(Fields.MANDATORY_FIELDS, to_save)

        for field_enum in Fields.OPTIONAL_SUB_FIELDS:
            if getattr(self, "_{}".format(field_enum)):
                to_save[field_enum] = {}
                self.save_fields(Fields.OPTIONAL_SUB_FIELDS[field_enum], to_save[field_enum])

        self.save_fields(Fields.OPTIONAL_FIELDS, to_save)            

        if self._topology != None:
            np_weights = self._model.get_weights()
            b64_encoded_w = []
            for w in np_weights:
                b64_encoded_w.append(MKO.b64encode_array(w))

            to_save[Fields.WEIGHTS] = b64_encoded_w
            to_save[Fields.TOPOLOGY] = self._topology

        return to_save
    
    def get_json(self) -> str:
        return json.dumps(self.get_dict())
    
    def __str__(self) -> str:
        return self.get_json()
        
    def __repr__(self) -> str:
        return self.get_json()

        