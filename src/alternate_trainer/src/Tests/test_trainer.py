import unittest
from src.MKO import MKO
import json
import os
import pandas as pd
import requests
import io
import numpy as np

class TestTrainer(unittest.TestCase):
    def __init__(self, *args):
        data_source = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        path_x = "test_data/data_x.csv"
        path_y = "test_data/data_y.csv"
        if not os.path.exists(path_x) or not os.path.exists(path_y):
            resp = input("Would you like to download data to '{}' ([y]/n): ".format(os.path.join(os.getcwd(), path_x))).lower()
            if resp == "n":
                exit(0)

            data = requests.get(data_source)
            str_io = io.StringIO("0,1,2,3,o\n{}".format(data.text))
            df = pd.read_csv(str_io)
            df = df.replace("Iris-setosa", 0)
            df = df.replace("Iris-versicolor", 1)
            df = df.replace("Iris-virginica", 2)

            def one_hot_encode(label):
                out = [0, 0, 0]
                out[label] = 1
                return out

            labels = [one_hot_encode(i) for i in df['o']]
            df2 = pd.DataFrame(labels)
            df = df.drop('o', axis=1)

            os.makedirs("test_data", exist_ok=True)
            with open(path_x, "w") as file:
                file.write(df.to_csv(index=False))

            with open(path_y, "w") as file:
                file.write(df2.to_csv(index=False))

        super().__init__(*args)
            

    def test_train(self):
        with open("test.json", 'r') as file:
            json_file = json.load(file)

        mko = MKO(json_file)
        mko.compile()
        mko.load_data()
        mko.train()
        inference_x = [5.9,3.0,5.1,1.8]
        gt = [0,0,1]
        inferences = mko.make_inference(inference_x,500)
        means = np.mean(inferences, axis=0)
        self.assertEqual(np.argmax(means), np.argmax(gt))

if __name__ == "__main__":
    unittest.main()