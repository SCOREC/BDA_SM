from typing import Optional


class Fields:
        MODEL_NAME = "model_name" #M
        TOPOLOGY = "topology" #O - s
        VERSION = "version" #M
        HYPER_PARAMS = "hyper_params" #O - e
        DATA = "data" #O - e
        WEIGHTS = "weights" #O - s
        TRAINED = "trained" #O - M
        LOSS = "loss" #O - M

        MANDATORY_FIELDS = {
            MODEL_NAME,
            VERSION,
        }

        LIST_FIELDS = {
            TOPOLOGY,
            WEIGHTS
        }

        DICT_FIELDS = {
            HYPER_PARAMS,
            DATA
        }

        class Data:
            DATA_TYPE = "data_type"
            LOCATION = "location"

            MANDATORY_FIELDS = {
                DATA_TYPE,
                LOCATION
            }

        class HyperParams:
            EPOCHS = "epochs"
            BATCH_SIZE = "batch_size"
            OPTIMIZER = "optimizer"
            DATA_SHAPE = "data_shape"
            LEARNING_RATE = "learning_rate"
            LOSS_FUNCTION = "loss_function"
            TRAIN_PERCENT= "train_percent"

            MANDATORY_FIELDS = {
                EPOCHS,
                BATCH_SIZE,
                OPTIMIZER,
                DATA_SHAPE,
                LEARNING_RATE,
                LOSS_FUNCTION,
                TRAIN_PERCENT
            }

        OPTIONAL_SUB_FIELDS = {
            DATA: Data,
            HYPER_PARAMS: HyperParams
        }

        OPTIONAL_FIELDS = {
            TRAINED,
            LOSS,
        }