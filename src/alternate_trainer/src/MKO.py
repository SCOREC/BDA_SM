import io
from typing import Any, Iterable, Tuple, Union
from src.json_parser import parse_json_model_structure
import json
import pickle
import numpy as np
import base64
import tensorflow as tf
from tensorflow.keras import backend as K
import pandas as pd
from src.exceptions import (
    InputException, 
    VersionException, 
    MKOTypeException, 
    InvalidArgument
)
from src.MKO_fields import Fields
from src.external_query import get_http, query_fetcher
import os

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
    def from_json(json_text: str) -> 'MKO':
        return MKO(json.loads(json_text))


    @staticmethod
    def from_empty(name: str) -> 'MKO':
        empty = {
            Fields.MODEL_NAME: name,
            Fields.VERSION: version
        }
        return MKO(empty)


    @staticmethod
    def enforce_type(data: Any, field: str, data_type: type):
        if type(data) != data_type:
            raise InputException(field, (type, type(data)))


    @staticmethod
    def enforce(field: str, input_params: dict):
        if field not in input_params:
            raise InputException(field)

        if field in Fields.LIST_FIELDS:
            MKO.enforce_type(input_params[field], field, list)

        if field in Fields.DICT_FIELDS:
            MKO.enforce_type(input_params[field], field, dict)


    @property
    def topographic(self) -> bool:
        return self._topology != None


    @property
    def augmented(self) -> bool:
        return self._data


    def parse_fields(self, fields: set, input_params: dict):
        for field in fields:
            MKO.enforce(field, input_params)
            setattr(self, "_{}".format(field), input_params[field])


    def validate_fetcher_format(self, data: dict):
        if self._data_type == Fields.Data.FETCHER:
                self.parse_fields(Fields.Data.MANDATORY_FETCHER_FIELDS, data)


    def parse_params(self, input_params: dict):
        self.parse_fields(Fields.MANDATORY_FIELDS, input_params)

        for field_enum in Fields.OPTIONAL_SUB_FIELDS:
            if field_enum in input_params:
                setattr(self, "_{}".format(field_enum), True)
                self.parse_fields(
                    Fields.OPTIONAL_SUB_FIELDS[field_enum].MANDATORY_FIELDS,
                    input_params[field_enum]
                )
            else:
                setattr(self, "_{}".format(field_enum), False)

        for field in Fields.OPTIONAL_FIELDS:
            if field in input_params:
                setattr(self, "_{}".format(field), input_params[field])

        if self.augmented:

            self.validate_fetcher_format(input_params[Fields.DATA])

        if Fields.TOPOLOGY in input_params:
            MKO.enforce(Fields.TOPOLOGY, input_params)
            self._topology = input_params[Fields.TOPOLOGY]
            if self._hyper_params == False:
                raise InputException(Fields.HYPER_PARAMS)
            
            self._model = parse_json_model_structure(
                self._data_shape, 
                self._model_name, 
                self._topology
            )
        else:
            self._topology = None

        if Fields.WEIGHTS in input_params:
            MKO.enforce(Fields.WEIGHTS, input_params)
            self._model.set_weights(
                [MKO.b64decode_array(w) for w in input_params[Fields.WEIGHTS]]
            )

        if version != self._version:
            raise VersionException(version, self._version)


    def add_hyper_params(self, hyper_params: Union[dict, str]):
        if type(hyper_params) == str:
            self.add_hyper_params(self, json.loads(hyper_params))

        MKO.enforce_type(hyper_params, "hyper_params", dict)

        self._hyper_params = True
        self.parse_fields(
            Fields.OPTIONAL_FIELDS[Fields.HYPER_PARAMS].MANDATORY_FIELDS, 
            hyper_params
        )


    def add_topology(self, topology: Union[list, str]):
        if self._hyper_params == False:
            raise Exception("hyper_parameters not defined, use 'add_hyper_params' before 'add_topology'")

        if type(topology) == str:
            self.add_topology(self, json.loads(topology))
            return

        MKO.enforce_type(topology, "topology", list)

        self._topology = topology
        self._model = parse_json_model_structure(
            self._data_shape, 
            self._model_name, 
            self._topology
        )


    def add_data(self, data: Union[dict, str]):
        if type(data) == str:
            self.add_data(json.loads(data))

        MKO.enforce_type(data, "data", list)
        self._data = True
        self.parse_fields(
            Fields.OPTIONAL_SUB_FIELDS[Fields.DATA].MANDATORY_FIELDS, 
            data
        )
        self.validate_fetcher_format(data)


    def compile(self):
        if not self.topographic:
            raise MKOTypeException("topographic")

        self._model.compile(loss=self._loss_function, optimizer=self._optimizer)
        K.set_value(self._model.optimizer.learning_rate, self._learning_rate)
        self._compiled = True


    def parse_data(self, df: pd.DataFrame) -> Tuple[np.array, np.array]:
        x = pd.DataFrame()
        y = pd.DataFrame()
        for col in df.columns:
            if col == "Time":
                continue

            if "F" in col:
                x[col] = df[col]
            if "T" in col:
                y[col] = df[col]

        return x.to_numpy(), y.to_numpy()


    def get_data_from_file(self, location: str) -> Tuple[np.array, np.array]:
        if not os.path.exists(location):
            raise FileNotFoundError("'{}' not found".format(location))

        with open(location, "r") as file:
            df = pd.read_csv(file)
    
        return self.parse_data(df)


    def get_data_from_http(self, location: str) -> Tuple[np.array, np.array]:
        df = pd.read_csv(io.StringIO(get_http(location)))
        return self.parse_data(df)


    def get_data_from_fetcher(self, location: str) -> pd.DataFrame:
        ids = self._x_tags + self._y_tags
        query = self._query_json
        query["tag_ids"] = ids # Remove string
        args = {
            Fields.Data.QUERY: query, 
            Fields.Data.AUTH: self._auth_json,
        }
        
        fetcher_data = query_fetcher(location, json.dumps(args))
        fetcher_json = json.loads(fetcher_data)
        data = np.array(fetcher_json["data"])
        df = pd.DataFrame(data=data, columns=fetcher_json["x_labels"], index=fetcher_json["y_labels"])
        return df[self._x_tags].to_numpy(), df[self._y_tags].to_numpy()

    def normalize(self, data: Iterable, is_x: bool = False, raise_if_none=False) -> np.array:
        data = np.array(data)

        
        if is_x:
            if self._x_mu is not None and self._x_std is not None:
                return (data - np.array(self._x_mu)) / np.array(self._x_std)

            if raise_if_none:
                if self._x_mu is None:
                    raise InputException(Fields.Data.X_MU)
                else:
                    raise InputException(Fields.Data.X_STD)
                    
        else:
            if self._y_mu is not None and self._y_std is not None:
                return (data - np.array(self._y_mu)) / np.array(self._y_std)

            if raise_if_none:
                if self._y_mu is None:
                    raise InputException(Fields.Data.Y_MU)
                else:
                    raise InputException(Fields.Data.Y_STD)
                    


        mu =  list(np.mean(data, axis=0))
        sigma = list(np.std(data, axis=0))

        if is_x:
            self._x_mu = mu
            self._x_std = sigma
        else:
            self._y_mu = mu
            self._y_std = sigma

        return self.normalize(data, is_x)

    def load_data(self):
        if not self.augmented:
            raise MKOTypeException("augmented")

        if self._data_type == Fields.Data.LOCAL:
            x, y = self.get_data_from_file(self._data_location)
        elif self._data_type == Fields.Data.HTTP:
            x, y = self.get_data_from_http(self._data_location)
        elif self._data_type == Fields.Data.FETCHER:
            x, y = self.get_data_from_fetcher(self._data_location)
        else:
            raise InvalidArgument(self._data_type, list(Fields.Data.DATA_TYPES))

        x = self.normalize(x, is_x=True)
        y = self.normalize(y)

        MKO.enforce_type(self._train_percent, Fields.HyperParams.TRAIN_PERCENT, float)

        index = int(self._train_percent * len(x))
        permutation = np.random.permutation(len(x))

        x = x[permutation]
        y = y[permutation]

        self._X_train = x[0:index]
        self._X_test = x[index:]
        self._Y_train = y[0:index]
        self._Y_test = y[index:]

        self._data_loaded = True


    def _trainable(self, throw_exceptions=True) -> bool:
        if throw_exceptions:
            if not self.topographic:
                raise MKOTypeException("topographic")

            if not self.augmented:
                raise MKOTypeException("augmented")

            if not self._data_loaded:
                raise Exception("data not loaded, call 'load_data' before 'train'")

            if not self._compiled:
                raise Exception("model not compiled, call 'compile' before 'train'")

            return True

        return self.topographic and self.augmented and self._data_loaded and self._compiled


    def train(self, verbose=0):
        if not self._trainable():
            return

        MKO.enforce_type(self._epochs, Fields.HyperParams.EPOCHS, int)
        MKO.enforce_type(self._batch_size, Fields.HyperParams.BATCH_SIZE, int)

        self._model.fit(
            self._X_train, 
            self._Y_train, 
            epochs=self._epochs, 
            batch_size=self._batch_size,
            verbose=verbose
        )
        self._loss = self._model.evaluate(
            self._X_test, 
            self._Y_test, 
            batch_size=self._batch_size,
            verbose=verbose
        )
        self._trained += self._epochs

    def evaluate(self, verbose=1):
        if not self._trainable():
            return

        MKO.enforce_type(self._batch_size, Fields.HyperParams.BATCH_SIZE, int)
        self._model.evaluate(
            self._X_test, 
            self._Y_test, 
            batch_size=self._batch_size,
            verbose=verbose
        )


    def make_inference(self, x: Iterable, samples: int) -> tf.Tensor:
        if not self.topographic:
            raise MKOTypeException("topographic")

        x = self.normalize(x, is_x=True, raise_if_none=True)

        X = tf.transpose(
                tf.reshape(
                    tf.repeat(x, repeats=samples), 
                    (len(x), samples)
                )
        )

        return self._model.predict(X)


    @staticmethod
    def b64decode_array(string: str) -> np.array:
        return pickle.loads(base64.b64decode(string))


    @staticmethod
    def b64encode_array(array: np.array) -> str:
        return base64.b64encode(
            pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
        ).decode('ascii')


    def save_fields(self, fields: set, to_save: dict):
        for field in fields:
            to_save[field] = getattr(self, "_{}".format(field))


    def get_dict(self) -> dict:
        to_save = {}
        self.save_fields(Fields.MANDATORY_FIELDS, to_save)

        for field_enum in Fields.OPTIONAL_SUB_FIELDS:
            if getattr(self, "_{}".format(field_enum)):
                to_save[field_enum] = {}
                self.save_fields(
                    Fields.OPTIONAL_SUB_FIELDS[field_enum].MANDATORY_FIELDS,
                    to_save[field_enum]
                )

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

        