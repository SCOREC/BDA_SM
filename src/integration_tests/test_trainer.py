from base64 import b64encode
from integration_tests.base_tm_rc import BaseTest
from integration_tests.helpers import format_params
import unittest
import json
import requests
import time
import copy
from trainer.src.MKO import MKO

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

        formatted_params = format_params("/get_status", params)


        time.sleep(20)
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(float(resp.text), 1)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)

        mko = MKO.from_b64str(json.loads(resp.text)["contents"])
        self.assertEqual(json.loads(mko._get_json())["model_name"], "models_name")

    def test_rc_alive(self):
        params = {
            "username": "person",
            "claim_check": "check"
        }

        formatted_params = format_params("/update_status", params)
        resp = requests.post(self.get_rc(formatted_params), data="0.5")
        self.assertEqual(resp.status_code, 200)

        formatted_params2 = format_params("/get_status", params)
        resp = requests.get(self.get_rc(formatted_params2))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, '0.5')



    def test_training(self):
        with open("trainer/test_fetcher.mko", "r") as file: # check if this exists before using
            test_mko = file.read()


        params = {
            "username": "person",
            "claim_check": "check2",
            "model_MKO": test_mko,
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
            print(resp.text)
            self.assertEqual(resp.status_code, 200)
            status = float(resp.text)
            time.sleep(1)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)
        
        # self.assertLessEqual(json.loads(json.loads(resp.text)["contents"])["loss"], 20)

    def test_add_data(self):
        with open("trainer/test_fetcher.json", "r") as file:
            test_json = file.read()

        full_json = json.loads(test_json)

        del full_json["hyper_params"]
        del full_json["topology"]

        original_json = copy.deepcopy(full_json)
        
        del full_json["data"]
        mko_data = b64encode(bytes(json.dumps(full_json), "utf-8"))

        params = {
            "username": "person",
            "claim_check": "check",
            "model_MKO": mko_data,
            "authenticator": original_json["data"]["auth_json"]["authenticator"],
            "password": original_json["data"]["auth_json"]["password"],
            "name": original_json["data"]["auth_json"]["name"],
            "role": original_json["data"]["auth_json"]["role"],
            "graphql_url": original_json["data"]["auth_json"]["url"],
            "x_tags": json.dumps(original_json["data"]["x_tags"]),
            "y_tags": json.dumps(original_json["data"]["y_tags"]),
            "start_time": original_json["data"]["query_json"]["start_time"],
            "end_time": original_json["data"]["query_json"]["end_time"],
            "data_location": original_json["data"]["data_location"],
            "result_cache_URI": self.get_rc()
        }

        formatted_params = format_params("/add_data", params)

        resp = requests.post(self.get_tm(formatted_params))
        self.assertEqual(resp.status_code, 200)

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
        
        new_mko_data = json.loads(resp.text)["contents"]
        mko_dict = json.loads(MKO.from_b64str(new_mko_data)._get_json())
        mko_prime_dict = json.loads(MKO(original_json)._get_json())
        self.assertEqual(mko_prime_dict, mko_dict)


    # def test_add_hp(self):
    #     self.add_test("hyper_params")

    # def test_add_top(self):
    #     self.add_test("topology")


if __name__ == "__main__":
    unittest.main()
