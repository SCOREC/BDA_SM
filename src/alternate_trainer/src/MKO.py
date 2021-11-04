from src.json_parser import parse_json_model_structure
import json
import pickle
import numpy as np
import base64
import tensorflow as tf
from tensorflow.keras import backend as K
import pandas as pd
from src.exceptions import InputException, VersionException

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
        TRAIN_PERCENT= "train_percent"

        WEIGHTS = "weights"
        TRAINED = "trained"
        LOSS = "loss"

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
            DATA_PATH,
            TRAIN_PERCENT,
            LEARNING_RATE,
        }

        LIST_FIELDS = {
            TOPOLOGY,
            WEIGHTS
        }

    def __init__(self, params: dict):
        self.parse_params(params)
        self._model = parse_json_model_structure(self._data_shape, self._model_name, self._topology)
        self._trained = False
        self._compiled = False
        self._loss = None
        self._data_loaded = False

    @staticmethod
    def from_MKO(mko: dict):
        mko_object = MKO(mko)
        MKO.enforce(MKO.Fields.WEIGHTS, mko)
        mko_object._model.set_weights([MKO.b64decode_array(w) for w in mko[MKO.Fields.WEIGHTS]])
        MKO.enforce(MKO.Fields.LOSS, mko)
        mko_object._loss = mko[MKO.Fields.LOSS]
        MKO.enforce(MKO.Fields.TRAINED, mko)
        mko_object._trained = mko[MKO.Fields.TRAINED]
        return mko_object

    @staticmethod
    def enforce(field: str, input_params: dict):
        if field not in input_params:
            raise InputException(field)

        if field in MKO.Fields.LIST_FIELDS and type(input_params[field]) != list:
            raise InputException(field, ("dict", type(input_params[field])))
    
    def parse_params(self, input_params: dict):
        for field in MKO.Fields.MANDATORY_FIELDS:
            MKO.enforce(field, input_params)
            setattr(self, "_{}".format(field), input_params[field])

        if version != self._version:
            raise VersionException(version, self._version)

    def compile(self):
        self._model.compile(loss=self._loss_function, optimizer=self._optimizer)
        K.set_value(self._model.optimizer.learning_rate, self._learning_rate)
        self._compiled = True

    def load_data(self): # TODO: implement data_descripter instead of path
        with open(self._data_path.format("x"), "r") as file:
            x = pd.read_csv(file).to_numpy()
        with open(self._data_path.format("y"), "r") as file:
            y = pd.read_csv(file).to_numpy()

        if type(self._train_percent) != float:
            raise InputException(MKO.Fields.TRAIN_PERCENT, ('float', type(self._train_percent)))
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
        if not self._data_loaded:
            raise Exception("data not loaded, call 'load_data' before 'train'")

        if not self._compiled:
            raise Exception("model not compiled, call 'compile' before train")

        if type(self._epochs) != int: # change to automattically enforce in Fields
            raise InputException(MKO.Fields.EPOCHS, ("int", type(self._epochs)))

        if type(self._batch_size) != int:
            raise InputException(MKO.Fields.BATCH_SIZE, ("int", type(self._batch_size)))

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

        to_save[MKO.Fields.TRAINED] = self._trained
        to_save[MKO.Fields.LOSS] = self._loss
        np_weights = self._model.get_weights()
        b64_encoded_w = []
        for w in np_weights:
            b64_encoded_w.append(MKO.b64encode_array(w))

        to_save[MKO.Fields.WEIGHTS] = b64_encoded_w

        return to_save
    
    def get_json(self) -> str:
        return json.dumps(self.get_dict())
    
    def __str__(self) -> str:
        return self.get_json()
        
    def __repr__(self) -> str:
        return self.get_json()

        