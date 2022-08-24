from re import A
import unittest
import requests
from server import claim_check
from server.config import TestingConfiguration as config
from server.claim_check import ClaimCheck
import time
from Tests.helpers import generate_string, get_test_set
from Tests.base import BaseTestCase
from urllib import parse
import json


class HeartbeatTestCase(BaseTestCase):
  def test_home_route(self):
    url = '/helloWorld'
    with self.client:
      response = self.client.get(url)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Hello World!' in response.get_data())

  def test_api_alive(self):
    url = '/api/helloWorld'
    with self.client:
      response = self.client.get(url)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Hello World!' in response.get_data())

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


    def test_new_claim_check(self):
      url = "/api/new_claim_check"
      with self.client:
        username_good = "good_user"
        username_bad = "bad_user"
        offset = 0
        query_string = {
          "username": username_good,
          "offset": offset
        }

        response = self.client.get(url, query_string=query_string)
        self.assert200(response)
        
        token = response.json['claim_check']
        claim_check = ClaimCheck.from_jwt(token)
        self.assertTrue(claim_check.is_valid(username_good))        
        self.assertFalse(claim_check.is_valid(username_bad))        

    def test_store_retrieve_data(self):
        username = "abcdefg"
        claim_check = ClaimCheck(username)
        generation_time = "1"
        original_data = generate_string(config.STRING_LEN_TEST, 1)[0]

        store_url = "/api/store_result"
        retrieve_url = "/api/get_result"
        with self.client:
            query_string = {
                'username': username,
                'claim_check': claim_check.token,
                'generation_time': generation_time
            }
            store_response = self.client.post(store_url, query_string=query_string, data=original_data)
            self.assert200(store_response)
            self.assertTrue(b'success' in store_response.data)

            query_string = {
                'username': username,
                'claim_check': claim_check.token,
                'please_retain': "True"
            }
            retrieve_response = self.client.get(retrieve_url, query_string=query_string)
            self.assert200(retrieve_response)
            retrieved_data = json.loads(retrieve_response.get_data())['contents']
            self.assertEqual(original_data, retrieved_data)

            del query_string['please_retain']
            retrieve_response = self.client.get(retrieve_url, query_string=query_string)
            self.assert200(retrieve_response)
            retrieved_data = json.loads(retrieve_response.get_data())['contents']
            self.assertEqual(original_data, retrieved_data)

            retrieve_response = self.client.get(retrieve_url, query_string=query_string)
            self.assertEqual(retrieve_response.status_code, 204)


    def test_store_retrieve_status(self):
        username = "abcdefg"
        claim_check = ClaimCheck(username)
        generation_time = "1"
        original_data = generate_string(config.STRING_LEN_TEST, 1)[0]
        status_string = "0.5"

        data_store_url = "/api/store_result"
        status_store_url = "/api/update_status"
        status_retrieve_url = "/api/get_status"
        with self.client:
            query_string = {
                'username': username,
                'claim_check': claim_check.token,
                'generation_time': generation_time
            }
            store_response = self.client.post(data_store_url, query_string=query_string, data=original_data)
            self.assert200(store_response)
            self.assertTrue(b'success' in store_response.data)

            query_string = {
                'username': username,
                'claim_check': claim_check.token,
            }
            store_status_response = self.client.post(status_store_url, query_string=query_string, data=status_string)
            self.assert200(store_status_response)

            retrieve_response = self.client.get(status_retrieve_url, query_string=query_string)
            self.assert200(retrieve_response)
            retrieved_status = retrieve_response.get_data().decode('utf-8')
            self.assertEqual(status_string, retrieved_status)


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
                self.assertEqual(json.loads(resp.content.decode("utf-8"))['contents'], expected[user][cc])

    def check_doesnt_exist(self, usernames, ccs):
        for user in usernames:
            for cc in ccs:
                self.assert404(self.get_data(user, cc))

    """
    def test_volume_api(self):
        usernames, ccs, data = get_test_set()
        expected = self.put_data_rest(usernames, ccs, data)
        self.check_eq_rest(usernames, ccs, expected)
        
    """

    """
    def test_purge_api(self):
        usernames, ccs, data = get_test_set()
        self.put_data_rest(usernames, ccs, data)
        time.sleep(8 * config.MIN_EXPIRY_TIME)
        self.check_doesnt_exist(usernames, ccs)
    """

    """
    def test_invalid_requests_put(self):
        origin = "/store_result"
        username = "abc"
        token = ClaimCheck(username).token

        # with none
        resp = self.client.post(origin)
        self.assert400(resp)

        # without cc
        params = {"username": username}
        param_formatted = self.format_params(origin, params)
        resp = self.client.post(param_formatted)
        self.assert400(resp)

        # non int gen time
        params = {"username": username, "claim_check": token, "generation_time": "not_a_number"}
        param_formatted = self.format_params(origin, params)
        resp = self.client.post(param_formatted)
        self.assert400(resp)

        # get instead of post
        params = {"username": username, "claim_check": token, "generation_time": 2}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert405(resp)

    """
    
    """
    def test_invalid_requests_get(self):
        origin = "/get_result"
        username_good = "abc"
        token_good = ClaimCheck(username_good).token
        username_bad = "none"
        token_bad = ClaimCheck(username_bad).token

        self.send_put(username_good, token_good, "50000", "")

        # no claim_check
        params = {"username": username_good}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert400(resp)

        # no username
        params = {"claim_check": token_good}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert400(resp)

        # user doesnt exist
        params = {"username": username_bad, "claim_check": token_good}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert404(resp)

        # claim_check doesnt exist
        params = {"username": username_good, "claim_check": token_bad}
        param_formatted = self.format_params(origin, params)
        resp = self.client.get(param_formatted)
        self.assert404(resp)

    def test_update_status(self):
        origin_1 = "/update_status"
        origin_2 = "/get_status"
        username = "abc"
        params = {
            "username": username,
            "claim_check": ClaimCheck(username).token
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

    """


if __name__ == "__main__":
    unittest.main()
    