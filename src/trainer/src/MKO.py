import io
from typing import Any, Iterable, Tuple, Union
from trainer.src.external_query import post_status
from trainer.src.json_parser import parse_json_model_structure
import json
import pickle
import numpy as np
import base64
import tensorflow as tf
from tensorflow.keras import backend as K
import pandas as pd
from trainer.src.training_callback import StatusCallback
from trainer.src.exceptions import (
    InputException, 
    VersionException, 
    MKOTypeException, 
    InvalidArgument
)
from trainer.src.MKO_fields import Fields
from trainer.src.external_query import get_http, query_fetcher
import os

version = "1.0"

class MKO:
    def __init__(self, params: dict):
        self._trained = 0
        self._data_loaded = False
        self._compiled = False
        self._loss = None
        self.parse_params(params)

    # string: string representing mko as b64 encoded json
    # generates mko from text
    @staticmethod
    def from_b64str(string: str) -> 'MKO':
        return MKO._from_json(base64.b64decode(string).decode("utf-8"))


    # json_text: string representing mko as json
    # generates mko from json text
    @staticmethod
    def _from_json(json_text: str) -> 'MKO':
        return MKO(json.loads(json_text))


    # name: name of the model
    # create base requirement mko from the name
    @staticmethod
    def from_empty(name: str) -> 'MKO':
        empty = {
            Fields.MODEL_NAME: name,
            Fields.VERSION: version
        }
        return MKO(empty)

    # data: data of type to check
    # field: name representing the data
    # data_type: type that the data must be
    # checks to ensure 'data' is type 'data_type'
    @staticmethod
    def enforce_type(data: Any, field: str, data_type: type):
        if type(data) != data_type:
            raise InputException(field, (type, type(data)))

    # field: field to check
    # input_params: location to check from
    # check if 'field' is in 'input_params'
    # also checks if the data is correct type
    # if list or dict
    @staticmethod
    def enforce(field: str, input_params: dict):
        if field not in input_params:
            raise InputException(field)

        if field in Fields.LIST_FIELDS:
            MKO.enforce_type(input_params[field], field, list)

        if field in Fields.DICT_FIELDS:
            MKO.enforce_type(input_params[field], field, dict)


    # does the mko have a model layout described
    @property
    def topographic(self) -> bool:
        return self._topology != None


    # does the mko have a data definition
    @property
    def augmented(self) -> bool:
        return self._data


    # fields: set of fields to parse
    # input_params: dict object to parse from
    # for each field in fields add the name of the field
    # as a parameter to store in self
    # eg. field = "x" then self._x = input_params["x"]
    def parse_fields(self, fields: set, input_params: dict):
        for field in fields:
            MKO.enforce(field, input_params)
            setattr(self, "_{}".format(field), input_params[field])


    # data: data descriptor
    # ensures that data descriptor for fetcher is correct
    def validate_fetcher_format(self, data: dict):
        if self._data_type == Fields.Data.FETCHER:
            self.parse_fields(Fields.Data.MANDATORY_FETCHER_FIELDS, data)


    # input_params: full json object
    # parse the json object into mko 
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


    # hyper_params: hyperparams to add
    # merges hyperparams with mko
    def add_hyper_params(self, hyper_params: Union[dict, str]):
        if type(hyper_params) == str:
            self.add_hyper_params(json.loads(hyper_params))
            return

        MKO.enforce_type(hyper_params, "hyper_params", dict)

        self._hyper_params = True
        self.parse_fields(
            Fields.OPTIONAL_SUB_FIELDS[Fields.HYPER_PARAMS].MANDATORY_FIELDS, 
            hyper_params
        )


    # topology: topology to add
    # merges topology with mko
    # must have data defined before
    def add_topology(self, topology: Union[list, str]):
        if self._hyper_params == False:
            raise Exception("hyper_parameters not defined, use 'add_hyper_params' before 'add_topology'")

        if type(topology) == str:
            self.add_topology(json.loads(topology))
            return

        MKO.enforce_type(topology, "topology", list)

        self._topology = topology
        self._model = parse_json_model_structure(
            self._data_shape, 
            self._model_name, 
            self._topology
        )


    # data: data descriptor to add
    # merges data with mko
    def add_data(self, data: Union[dict, str]):
        if type(data) == str:
            self.add_data(json.loads(data))
            return

        self._data = True
        self.parse_fields(
            Fields.OPTIONAL_SUB_FIELDS[Fields.DATA].MANDATORY_FIELDS, 
            data
        )
        self.validate_fetcher_format(data)


    # compiles the model
    def compile(self):
        if not self.topographic:
            raise MKOTypeException("topographic")

        self._model.compile(loss=self._loss_function, optimizer=self._optimizer)
        K.set_value(self._model.optimizer.learning_rate, self._learning_rate)
        self._compiled = True


    # df: dataframe of data
    # parses csv data to be used by the model
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

    # location: file location
    # reads csv from file
    def get_data_from_file(self, location: str) -> Tuple[np.array, np.array]:
        if not os.path.exists(location):
            raise FileNotFoundError("'{}' not found".format(location))

        with open(location, "r") as file:
            df = pd.read_csv(file)
    
        return self.parse_data(df)


    # location: request location
    # gets data from http request and parses
    def get_data_from_http(self, location: str) -> Tuple[np.array, np.array]:
        df = pd.read_csv(io.StringIO(get_http(location)))
        return self.parse_data(df)

    # location: fetcher server location
    # requests data from fetcher and parses
    def get_data_from_fetcher(self, location: str) -> pd.DataFrame:
        ids = self._x_tags + self._y_tags
        query = self._query_json
        query["tag_ids"] = ids
        args = {
            Fields.Data.QUERY: query, 
            Fields.Data.AUTH: self._auth_json,
        }
        
        fetcher_data = query_fetcher(location, json.dumps(args))
        fetcher_json = json.loads(fetcher_data)
        data = np.array(fetcher_json["data"])
        df = pd.DataFrame(data=data, columns=fetcher_json["x_labels"], index=fetcher_json["y_labels"])
        return df[self._x_tags].to_numpy(), df[self._y_tags].to_numpy()

    # data: dataset
    # is_x: is the data x if not y
    # reverse: should de-normalize
    # raise_if_none: if mu or std not defined raise exception
    # normalizes / de-normalized data, calculates mu and std if none
    def normalize(self, data: Iterable, is_x: bool = False, reverse: bool = False, raise_if_none: bool = False) -> np.array:
        data = np.array(data)

        if reverse:
            raise_if_none = True

        if is_x:
            if self._x_mu is not None and self._x_std is not None:
                if not reverse:
                    return (data - np.array(self._x_mu)) / np.array(self._x_std)
                else:
                    return data * np.array(self._x_std) + np.array(self._x_mu)

            if raise_if_none:
                if self._x_mu is None:
                    raise InputException(Fields.Data.X_MU)
                else:
                    raise InputException(Fields.Data.X_STD)
                    
        else:
            if self._y_mu is not None and self._y_std is not None:
                if not reverse:
                    return (data - np.array(self._y_mu)) / np.array(self._y_std)
                else:
                    return data * np.array(self._y_std) + np.array(self._y_mu)

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

    # loads data according to data descriptor
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

    # throw_exceptions: should throw exceptions if true
    # is trainable
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


    # verbose: how much should be printed
    # push_update_args: should push updates to resultCache
    # train the model if trainable
    def train(self, verbose: int = 0, push_update_args: tuple = None):
        if not self._trainable():
            return

        MKO.enforce_type(self._epochs, Fields.HyperParams.EPOCHS, int)
        MKO.enforce_type(self._batch_size, Fields.HyperParams.BATCH_SIZE, int)

        callbacks = []
        if push_update_args:
            post_status(*push_update_args, 0)
            callbacks = [StatusCallback(push_update_args, self._epochs)]

        self._model.fit(
            self._X_train, 
            self._Y_train, 
            epochs=self._epochs, 
            batch_size=self._batch_size,
            verbose=verbose,
            callbacks=callbacks
        )

        self._loss = self._model.evaluate(
            self._X_test, 
            self._Y_test, 
            batch_size=self._batch_size,
            verbose=verbose
        )

        self._trained += self._epochs

    # verbose: how much is printed
    # evaluates the model
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


    # x: input data
    # samples: number of times to run interation
    # use variational dropout to approximate distribution
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

        return self.normalize(self._model.predict(X), reverse=True)


    # return unpickled version of string
    @staticmethod
    def b64decode_array(string: str) -> np.array:
        return pickle.loads(base64.b64decode(string))


    # return pickled version of array
    @staticmethod
    def b64encode_array(array: np.array) -> str:
        return base64.b64encode(
            pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
        ).decode('ascii')


    # fields: fields to save
    # to_save: json object
    # for each filed in fields save in json object
    def save_fields(self, fields: set, to_save: dict):
        for field in fields:
            to_save[field] = getattr(self, "_{}".format(field))


    # get json object representation of mko
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


    # get string json string representation of mko
    def _get_json(self) -> str:
        return json.dumps(self.get_dict())
    
    def get_b64(self) -> str:
        json_str = self._get_json()
        return base64.b64encode(bytes(json_str, "utf-8")).decode("utf-8")

    # returns b64 encoded string
    def __str__(self) -> str:
        return self.get_b64()
        
        
    # returns b64 encoded string
    def __repr__(self) -> str:
        return self.get_b64()
        