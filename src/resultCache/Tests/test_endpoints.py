from calendar import c
import unittest
import requests
from resultCache.config import TestConfig as config
import time
from resultCache.Tests.helpers import generate_string, get_test_set
from resultCache.Tests.base import BaseTestCase
from urllib import parse
import json

class EndpointTests(BaseTestCase):
    def format_params(self, endpoint, params):
        parsed = parse.urlparse(endpoint)
        encoded_params = parse.urlencode(params)
        parsed = parsed._replace(query=encoded_params)
        return parse.urlunparse(parsed)

    def send_put(self, username, claim_check, generation_time, data) -> requests.Response:
        params = {"username": username, "claim_check": claim_check, "generation_time": generation_time}
        endpoint = self.format_params("/store_result", params)
        return self.client.post(endpoint, data=data)

    def get_data(self, username, claim_check) -> requests.Response:
        params = {"username": username, "claim_check": claim_check}
        endpoint = self.format_params("/get_result", params)
        return self.client.get(endpoint)

    def test_basic_rest_api(self):
        username = "abcdefg"
        claim_check = "1234567"
        generation_time = "1"
        data = generate_string(config.string_len_test, 1)[0]

        self.send_put(username, claim_check, generation_time, data)

        resp = self.get_data(username, claim_check)
        out = json.loads(resp.data.decode("utf-8"))['contents']
        self.assertEqual(out, data)


    def put_data_rest(self, usernames, ccs, data):
        expected = {}
        data_index = 0
        for user in usernames:
            expected[user] = {}
            for cc in ccs:
                datum = data[data_index]
                self.send_put(user, cc, 0, datum)
                expected[user][cc] = datum
                data_index += 1

        return expected

    def check_eq_rest(self, usernames, ccs, expected):
        for user in usernames:
            for cc in ccs:
                resp = self.get_data(user, cc)
                self.assert200(resp)
                self.assertEqual(json.loads(resp.data.decode("utf-8"))['contents'], expected[user][cc])

    def check_doesnt_exist(self, usernames, ccs):
        for user in usernames:
            for cc in ccs:
                self.assert404(self.get_data(user, cc))

    def test_volume_api(self):
        usernames, ccs, data = get_test_set()
        expected = self.put_data_rest(usernames, ccs, data)
        self.check_eq_rest(usernames, ccs, expected)
        

    def test_purge_api(self):
        usernames, ccs, data = get_test_set()
        self.put_data_rest(usernames, ccs, data)
        time.sleep(8 * config.min_expiry_time)
        self.check_doesnt_exist(usernames, ccs)

    def test_invalid_requests_put(self):
        origin = "/store_result"

        # with none
        resp = self.client.post(origin)
        self.assert400(resp)

        # without cc
        params = {"username": "abc"}
        param_formatted = self.format_params(origin, params)
        resp = self.client.post(param_formatted)
        self.assert400(resp)

        # non int gen time
        params = {"username": "abc", "claim_check": "efg", "generation_time": "not_a_number"}
        param_formatted = self.format_params(origin, params)
        resp = self.client.post(param_formatted)
        self.assert400(resp)

        # get instead of post
        params = {"username": "abc", "claim_check": "efg", "generation_time": 2}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert405(resp)

    
    def test_invalid_requests_get(self):
        origin = "/get_result"
        username = "abc"
        claim_check = "gre"
        username_non_existent = "none"
        claim_check_non_existent = "notExisting"

        self.send_put(username, claim_check, "50000", "")

        # no claim_check
        params = {"username": username}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert400(resp)

        # no username
        params = {"claim_check": claim_check}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert400(resp)

        # user doesnt exist
        params = {"username": username_non_existent, "claim_check": claim_check}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert404(resp)

        # claim_check doesnt exist
        params = {"username": username, "claim_check": claim_check_non_existent}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert404(resp)

    def test_update_status(self):
        origin_1 = "/update_status"
        origin_2 = "/get_status"
        params = {
            "username": "abc",
            "claim_check": "few"
        }
        p1 = self.format_params(origin_1, params)
        p2 = self.format_params(origin_2, params)
        resp = self.client.post(p1, data="0.1")
        self.assert200(resp)
        resp = self.client.get(p2)
        self.assert200(resp)
        self.assertEqual(resp.data.decode("utf-8"), "0.1")
        self.send_put(params["username"], params["claim_check"], 1, "hi")
        resp = self.client.get(p2)
        self.assert200(resp) 
        self.assertEqual(resp.data.decode("utf-8"), "1.0")
        self.get_data(params["username"], params["claim_check"])
        resp = self.client.get(p2)
        self.assert404(resp)



if __name__ == "__main__":
    unittest.main()
    