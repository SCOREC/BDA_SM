class Defaults:
    layers = 2 # hidden layers
    activation_funct = "relu"
    units = 128
    dropout_rate = 0.95

    epochs = 200
    batch_size = 64
    optimizer = "adam"
    learning_rate = 0.001
    train_percent = 0.9
    loss_function = "mse"

    @staticmethod
    def get_fetcher_data_json(authenticator, password, name, role, auth_url, x_tags, y_tags, start_time, end_time, data_location):
        """
        "data": {
            "x_mu": null,
            "x_std": null,
            "y_mu": null,
            "y_std": null,
            "data_type": "fetcher",
            "auth_json" : {
                "authenticator": "kaushp",
                "password": "welcome001",
                "name": "kaushp",
                "role": "rpi_ro_group",
                "url": "https://rpi.cesmii.net/graphql"
            },
            "x_tags": ["984"],
            "y_tags": ["983", "985"],
            "query_json" : {
                "start_time": "2020-01-23T20:51:40.071032+00:00",
                "end_time": "now",
                "GMT_prefix_sign":"plus",
                "max_samples": 0
            },
            "data_location": "http://127.0.0.1:8000"
        }"""

        return {
            "x_mu": None,
            "x_std": None,
            "y_mu": None,
            "y_std": None,
            "data_type": "fetcher",
            "auth_json" : {
                "authenticator": authenticator,
                "password": password,
                "name": name,
                "role": role,
                "url": auth_url,
            },
            "x_tags": x_tags,
            "y_tags": y_tags,
            "query_json" : {
                "start_time": start_time,
                "end_time": end_time,
                "GMT_prefix_sign":"plus",
                "max_samples": 0
            },
            "data_location": data_location
        }

    @staticmethod
    def get_hparams_json(loss_function, data_shape, epochs, batch_size, optimizer, learning_rate, train_percent):
        """
        "hyper_params": {
            "epochs": 300,
            "batch_size": 64,
            "data_shape": [1],
            "optimizer": "adam",
            "learning_rate": 0.001,
            "loss_function": "mse",
            "train_percent": 0.9
        },"""

        epochs = epochs if epochs != None else Defaults.epochs
        batch_size = batch_size if batch_size != None else Defaults.batch_size
        optimizer = optimizer if optimizer != None else Defaults.optimizer
        learning_rate = learning_rate if learning_rate != None else Defaults.learning_rate
        train_percent = train_percent if train_percent != None else Defaults.train_percent
        loss_function = loss_function if loss_function != None else Defaults.loss_function

        return {
            "epochs": epochs,
            "batch_size": batch_size,
            "data_shape": data_shape,
            "optimizer": optimizer,
            "learning_rate": learning_rate,
            "loss_function": loss_function,
            "train_percent": train_percent,
        }

        

    @staticmethod
    def get_topology_json(output_shape, final_activation_funct, layers, activation_funct, units, dropout_rate):
        """
        "topology": [
            {
                "type": "dense",
                "activation": "relu",
                "units": 512
            }, {
                "type": "dropout",
                "rate": 0.95
            }, {
                "type": "dense",
                "activation": "relu",
                "units": 2
            }
        ],"""

        layers = layers if layers != None else Defaults.layers
        activation_funct = activation_funct if activation_funct != None else Defaults.activation_funct
        units = units if units != None else Defaults.units
        dropout_rate = dropout_rate if dropout_rate != None else Defaults.dropout_rate
        final_activation_funct = final_activation_funct if final_activation_funct != None else activation_funct

        out = []

        for _ in range(layers):
            out.append({
                "type": "dense",
                "activation": activation_funct,
                "units": units,
            })

            out.append({
                "type": "dropout",
                "rate": dropout_rate
            })

        out.append({
            "type": "dense",
            "activation": final_activation_funct,
            "units": output_shape
        })

        return out

    




