from server.config import ExternalsConfig as cfg

stub = {
  "model_name": "REQUIRED",
  "version": "1.0",
}

topology = [
  {
    "type": "dense",
    "activation": "relu",
    "units": 50
  }, {
    "type": "dropout",
    "rate": 0.95
  }, {
    "type": "dense",
    "activation": "relu",
    "units": "50"
  }
]

hypers = {
  "epochs": 300,
  "batch_size": 64,
  "data_shape": [1],
  "optimizer": "adam",
  "learning_rate": 0.001,
  "loss_function": "mse",
  "train_percent": 0.9,
  "trained": 0
}

dataspec = {
  "time_as_input" : False,
  "inputs": "REQUIRED",
  "outputs": "REQUIRED",
  "query_json" : {
    "start_time": "REQUIRED",
    "end_time": "REQUIRED",
    "period": "36000",
    "max_samples": 0
  },
  "data_type": "fetcher",
  "data_location" : "REQUIRED_SMIP_URL"
}
