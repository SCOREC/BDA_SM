import unittest
from uuid import uuid4
from base_inference_manager import BaseTest
from trainer.src.MKO import MKO
from sampler import app
from urllib import parse
from helpers import format_params
import numpy as np
import requests
import json
import time

class InferenceManagerTests(BaseTest):
    def __init__(self):
        self.mko = "" # TODO: load sample mko
        self.username = str(uuid4())

    def format_params(self, endpoint, params):
        parsed = parse.urlparse(endpoint)
        encoded_params = parse.urlencode(params)
        parsed = parsed._replace(query=encoded_params)
        return parse.urlunparse(parsed)
        
    def post_im(self, endpoint, params):
        formatted_params = format_params(endpoint, params)
        requests.post(self.get_im(formatted_params))

    def get_rc(self, username, cc, update_time=0.1):
        params = {
            "username": username,
            "claim_check": cc
        }

        formatted_params = format_params("/get_status", params)

        status = 0
        while status != 1:
            resp = requests.get(self.get_rc(formatted_params))
            self.assertEqual(resp.status_code, 200)
            status = float(resp.text)
            time.sleep(update_time)

        formatted_params = format_params("/get_result", params)
        
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)
        return resp.text

    def get_cc(self, username):
        params = {
            "username": username
        }

        formatted_params = format_params("/get_cc", params)
        resp = requests.get(self.get_rc(formatted_params))
        self.assertEqual(resp.status_code, 200)
        return resp.text

    def sample_sampler(self):
        pass
    #     sample_num = None
    #     data_array = None
    #     claim_check = self.get_cc(self.username)

    #     params = {
    #         "data_array": data_array,
    #         "model_mko": self.mko,
    #         "sample_num": sample_num,
    #         "sampler_uri": self.get_sm(),
    #         "rc_uri": self.get_rc(),
    #         "username": self.username,
    #         "claim_check": claim_check
    #     }

    #     resp = self.post_im("/Infer/sample", params)
    #     self.assertEqual(resp.status_code, 200)

    def test_sample(self):
        sample_num = None
        data_array = None
        claim_check = self.get_cc(self.username)

        params = {
            "data_array": data_array,
            "model_mko": self.mko,
            "sample_num": sample_num,
            "sampler_uri": self.get_sm(),
            "rc_uri": self.get_rc(),
            "username": self.username,
            "claim_check": claim_check
        }

        resp = self.post_im("/Infer/sample", params)
        self.assertEqual(resp.status_code, 200)
        time.sleep(1)
        results = self.get_rc(self.username, claim_check)
        self.assertEqual(results, self.sample_sampler)

    def test_stat(self):
        data_array = None
        claim_check = self.get_cc(self.username)

        params = {
            "data_array": data_array,
            "model_mko": self.mko,
            "sampler_uri": self.get_sm(),
            "rc_uri": self.get_rc(),
            "username": self.username,
            "claim_check": claim_check
        }

        resp = self.post_im("/Analyze/stat", params)
        self.assertEqual(resp.status_code, 200)
        time.sleep(1)
        gt = None
        pred = np.array(json.loads(self.get_rc(self.username, claim_check)))
        self.assertTrue(np.allclose(gt, pred))

    def test_integrator(self):
        sample_num = None
        data_array = None
        claim_check = self.get_cc(self.username)

        params = {
            "data_array": data_array,
            "model_mko": self.mko,
            "sample_num": sample_num,
            "sampler_uri": self.get_sm(),
            "rc_uri": self.get_rc(),
            "username": self.username,
            "claim_check": claim_check
        }

        resp = self.post_im("/Analyze/Integrator", params)
        self.assertEqual(resp.status_code, 200)
        time.sleep(20)
        gt = None
        pred = json.loads(self.get_rc(self.username, claim_check))
        self.assertTrue(np.allclose([gt], [pred]))


if __name__ == "__main__":
    unittest.main()