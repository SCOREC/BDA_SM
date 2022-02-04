import unittest
from trainer.src.MKO import MKO
import json
import os
import pandas as pd
import requests
import io
import numpy as np
from trainer.src.Tests.data_2_saver import data_2

class TestTrainer(unittest.TestCase):
    def __init__(self, *args):
        data_source = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        path = ".test_data/data.csv"
        if not os.path.exists(path):
            resp = input("Would you like to download data to '{}' ([y]/n): ".format(os.path.join(os.getcwd(), path))).lower()
            if resp == "n":
                exit(0)

            data = requests.get(data_source)
            str_io = io.StringIO("F0,F1,F2,F3,o\n{}".format(data.text))
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

            for i, col in enumerate(df2):
                df["T{}".format(i)] = df2[col]

            os.makedirs(".test_data", exist_ok=True)
            with open(path, "w") as file:
                file.write(df.to_csv(index=False))

            with open(".test_data/data_2.csv", "w") as file:
                file.write(data_2)
                
        super().__init__(*args)

    def train_model(self, filename):
        with open(filename, 'r') as file:
            json_file = json.load(file)

        mko = MKO(json_file)
        mko.compile()
        mko.load_data()
        mko.train()
        return mko

    def test_train(self):
        mko = self.train_model("trainer/test.json")
        inference_x = [5.9,3.0,5.1,1.8]
        gt = [0,0,1]
        inferences = mko.make_inference(inference_x, 500)
        means = np.mean(inferences, axis=0)
        print(means)
        self.assertEqual(np.argmax(means), np.argmax(gt))

    def test_train_2(self):
        mko = self.train_model("trainer/test_2.json")
        inference_x = [5.127105236,1.958719381]
        gt = [25.24810875,34.65854027,28.23331668]
        inferences = mko.make_inference(inference_x, 500)
        means = np.mean(inferences, axis=0)
        self.assertTrue(np.allclose(means, gt, atol=5))

if __name__ == "__main__":
    unittest.main()