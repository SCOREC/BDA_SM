
def create_test_input(filename="/tmp/testInput.json"):
  with open(filename, "w") as fd:
    fd.write("""
{
 "version": 1.0,
 "modelname": "syn4",
 "savefile": "/tmp/savefile",
 "training_controls":{
  "learning_rate": 0.01,
  "training_set_fraction": 0.8,
  "testing_set_fraction": 0.15,
  "batch_size": 32,
  "epochs": 10
 },
 "model_structure": {
    "nInputs": 3,
    "nOutputs": 1,
    "nLayers": 2,
    "defaults": {
      "type": "Dense",
      "units": 5,
      "activation": "tanh",
      "rate": 0.95,
      "lambda": 1.0e-6
    },
    "layers": [
      {
        "name": "layer01",
        "type": "Dense",
        "units": 5,
        "activation": "relu"
      },
      {
        "name": "layer02",
        "type": "variationalDropout",
        "rate": 0.95
      },
      {
        "name": "layer03",
        "type": "Dense",
        "units": 5,
        "activation": "relu"
      },
      {
        "name": "output",
        "type": "Dense",
        "units": 1
      }
    ]
  },
  "data_descriptor":{
    "type": "http",
    "URL": "http://127.0.0.1:8181/get-csv/test4",
    "input_features": 3,
    "output_features" : 1,
    "server_name": "",
    "server_JWT": "",
    "server_URI": "",
    "tag_ids": [],
    "attr_ids": [],
    "start_time": null,
    "end_time": null,
    "max_samples": null,
    "offset": 0
  }
}
""")
