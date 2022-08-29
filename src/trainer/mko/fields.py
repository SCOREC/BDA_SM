class Fields:
        MODEL_NAME = "model_name"
        TOPOLOGY = "topology"
        VERSION = "version"
        HYPER_PARAMS = "hyper_params"
        DATA = "data"
        WEIGHTS = "weights" 
        TRAINED = "trained"
        LOSS = "loss"

        class Data:
            DATA_TYPE = "data_type"
            LOCATION = "data_location"
            FETCHER = "fetcher"
            LOCAL = "local"
            HTTP = "http"
            AUTH = "auth_json"
            QUERY = "query_json"
            X_TAGS = "x_tags"
            Y_TAGS = "y_tags"
            X_MU = "x_mu"
            X_STD = "x_std"
            Y_MU = "y_mu"
            Y_STD = "y_std"

            DATA_TYPES = {
                LOCAL,
                HTTP,
                FETCHER
            }

            MANDATORY_FIELDS = {
                DATA_TYPE,
                LOCATION,
                X_MU,
                X_STD,
                Y_MU,
                Y_STD
            }

            MANDATORY_FETCHER_FIELDS = {
                AUTH,
                QUERY,
                X_TAGS,
                Y_TAGS
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

        MANDATORY_FIELDS = {
            MODEL_NAME,
            VERSION,
        }

        LIST_FIELDS = {
            TOPOLOGY,
            WEIGHTS,
            HyperParams.DATA_SHAPE
        }

        DICT_FIELDS = {
            HYPER_PARAMS,
            DATA,
            Data.AUTH,
            Data.QUERY
        }

        OPTIONAL_SUB_FIELDS = {
            DATA: Data,
            HYPER_PARAMS: HyperParams
        }

        OPTIONAL_FIELDS = {
            TRAINED,
            LOSS,
        }
        