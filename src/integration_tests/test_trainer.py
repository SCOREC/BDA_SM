from integration_tests.base import BaseTest
from integration_tests.helpers import format_params
import unittest
import json
import requests
import time
import copy

class TrainerTests(BaseTest):
    def test_mko_creation(self):
        params = {
            "username": "person",
            "claim_check": "check",
            "model_name": "models_name",
            "result_cache_URI": self.get_rc()
        }

        formatted_params = format_params("/create_MKO", params)

        resp = requests.post(self.get_tm(formatted_params))
        self.assertEqual(resp.status_code, 200)

        del params["model_name"]
        del params["result_cache_URI"]

        formatted_params = format_params("/get_status", params)


        time.sleep(20)
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(float(resp.text), 1)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)

        
        self.assertEqual(json.loads(json.loads(resp.text)["contents"])["model_name"], "models_name")

    def test_training(self):
        with open("trainer/test_2.json", "r") as file: # check if this exists before using
            test_json = file.read()


        params = {
            "username": "person",
            "claim_check": "check",
            "model_MKO": test_json,
            "result_cache_URI": self.get_rc()
        }

        formatted_params = format_params("/train", params)

        resp = requests.post(self.get_tm(formatted_params))
        self.assertEqual(resp.status_code, 200)

        del params["model_MKO"]
        del params["result_cache_URI"]

        formatted_params = format_params("/get_status", params)

        time.sleep(20)
        status = 0
        while status != 1:
            resp = requests.get(self.get_rc(formatted_params))
            self.assertEqual(resp.status_code, 200)
            status = float(resp.text)
            time.sleep(1)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)
        
        self.assertLessEqual(json.loads(json.loads(resp.text)["contents"])["loss"], 20)

    def add_test(self, add_type):
        with open("trainer/test.json", "r") as file: # check if this exists before using
            test_json = file.read()


        full_json = json.loads(test_json)

        original_json = copy.deepcopy(full_json)


        if add_type == "hyper_params":
            del original_json["topology"]

        del original_json[add_type]

        to_add_json = full_json[add_type]

        params = {
            "username": "person",
            "claim_check": "check",
            "model_MKO": json.dumps(original_json),
            "to_add": json.dumps(to_add_json),
            "type": add_type,
            "result_cache_URI": self.get_rc()
        }

        formatted_params = format_params("/add_component", params)

        resp = requests.post(self.get_tm(formatted_params))
        self.assertEqual(resp.status_code, 200)

        del params["model_MKO"]
        del params["result_cache_URI"]
        del params["to_add"]
        del params["type"]

        formatted_params = format_params("/get_status", params)

        time.sleep(20)
        status = 0
        while status != 1:
            resp = requests.get(self.get_rc(formatted_params))
            self.assertEqual(resp.status_code, 200)
            status = float(resp.text)
            time.sleep(1)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)
        
        self.assertTrue(add_type in json.loads(json.loads(resp.text)['contents']))

    def test_add_data(self):
        self.add_test("data")

    def test_add_hp(self):
        self.add_test("hyper_params")

    def test_add_top(self):
        self.add_test("topology")


if __name__ == "__main__":
    unittest.main()