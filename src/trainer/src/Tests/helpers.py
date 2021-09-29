
def create_test_input(filename="/tmp/testInput.json", dropout_rate=1.0):
  with open(filename, "w") as fd:
    fd.write(f"""
{{
 "version": 1.0,
 "modelname": "syn4",
 "savefile": "/tmp/savefile",
 "training_controls":{{
  "learning_rate": 0.001,
  "training_set_fraction": 0.8,
  "testing_set_fraction": 0.15,
  "batch_size": 10,
  "epochs": 100
 }},
 "model_structure": {{
    "nInputs": 2,
    "nOutputs": 1,
    "nLayers": 2,
    "defaults": {{
      "type": "Dense",
      "units": 15,
      "activation": "tanh",
      "rate": 0.95,
      "lambda": 1.0e-6
    }},
    "layers": [
      {{
        "name": "layer01",
        "type": "Dense",
        "units": 25,
        "activation": "relu"
      }},
      {{
        "name": "layer02",
        "type": "variationalDropout",
        "rate": {dropout_rate}
      }},
      {{
        "name": "layer03",
        "type": "Dense",
        "units": 25,
        "activation": "relu"
      }},
      {{
        "name": "output",
        "type": "Dense",
        "units": 1
      }}
    ]
  }},
  "data_descriptor":{{
    "type": "http",
    "URL": "http://127.0.0.1:8181/get-csv/test2",
    "input_features": 2,
    "output_features" : 1,
    "server_name": "",
    "server_JWT": "",
    "server_URI": "",
    "tag_ids": [],
    "attr_ids": [],
    "start_time": null,
    "end_time": null,
    "max_samples": null,
    "offset": 0,
    "testing_predictions": [ [[0.5, 0.0], [0.3, 0.3]], [[0.25], [0.3]] ]
  }}
}}
""")

