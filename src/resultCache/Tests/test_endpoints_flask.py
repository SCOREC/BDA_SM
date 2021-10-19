# import unittest
# import requests
# from resultCache.config import TestConfig as config
# import time
# from resultCache.Tests.helpers import generate_string, get_test_set

# class EndpointTests(unittest.TestCase):
#     def send_put(self, username, claim_check, generation_time, data) -> requests.Response:
#         params = {"username": username, "claim_check": claim_check, "generation_time": generation_time}
#         return requests.post("http://127.0.0.1:5000/store_result", data=data, params=params)

#     def get_data(self, username, claim_check) -> requests.Response:
#         params = {"username": username, "claim_check": claim_check}
#         return requests.get("http://127.0.0.1:5000/get_result", params=params)

#     def kill_server(self):
#         requests.post("http://127.0.0.1:5000/close")

#     def test_basic_rest_api(self):
#         username = "abcdefg"
#         claim_check = "1234567"
#         generation_time = "1"
#         data = generate_string(config.string_len_test, 1)[0]

#         self.send_put(username, claim_check, generation_time, data)

#         resp = self.get_data(username, claim_check)
#         self.assertEqual(resp.text, data)


#     def put_data_rest(self, usernames, ccs, data):
#         expected = {}
#         data_index = 0
#         for user in usernames:
#             expected[user] = {}
#             for cc in ccs:
#                 datum = data[data_index]
#                 self.send_put(user, cc, 0, datum)
#                 expected[user][cc] = datum
#                 data_index += 1

#         return expected

#     def check_eq_rest(self, usernames, ccs, expected):
#         for user in usernames:
#             for cc in ccs:
#                 resp = self.get_data(user, cc)
#                 self.assertEqual(resp.status_code, 200)
#                 self.assertEqual(resp.text, expected[user][cc])

#     def check_doesnt_exist(self, usernames, ccs):
#         for user in usernames:
#             for cc in ccs:
#                 self.assertEqual(self.get_data(user, cc).status_code, 404)

#     def test_volume_api(self):
#         usernames, ccs, data = get_test_set()
#         expected = self.put_data_rest(usernames, ccs, data)
#         self.check_eq_rest(usernames, ccs, expected)
        

#     def test_purge_api(self):
#         usernames, ccs, data = get_test_set()
#         self.put_data_rest(usernames, ccs, data)
#         time.sleep(4 * config.min_expiry_time)
#         self.check_doesnt_exist(usernames, ccs)

#     def test_invalid_requests_put(self):
#         origin = "http://127.0.0.1:5000/store_result"

#         # with none
#         resp = requests.post(origin)
#         self.assertEqual(resp.status_code, 400)

#         # without cc
#         params = {"username": "abc"}
#         resp = requests.post(origin, params=params)
#         self.assertEqual(resp.status_code, 400)

#         # non int gen time
#         params = {"username": "abc", "claim_check": "efg", "generation_time": "not_a_number"}
#         resp = requests.post(origin, params=params)
#         self.assertEqual(resp.status_code, 400)

#         # get instead of post
#         params = {"username": "abc", "claim_check": "efg", "generation_time": 2}
#         resp = requests.get(origin, params=params)
#         self.assertEqual(resp.status_code, 405)

    
#     def test_invalid_requests_get(self):
#         origin = "http://127.0.0.1:5000/get_result"
#         username = "abc"
#         claim_check = "gre"
#         username_non_existent = "none"
#         claim_check_non_existent = "notExisting"

#         self.send_put(username, claim_check, "50000", "")

#         # no claim_check
#         params = {"username": username}
#         resp = requests.get(origin, params=params)
#         self.assertEqual(resp.status_code, 400)

#         # no username
#         params = {"claim_check": claim_check}
#         resp = requests.get(origin, params=params)
#         self.assertEqual(resp.status_code, 400)

#         # user doesnt exist
#         params = {"username": username_non_existent, "claim_check": claim_check}
#         resp = requests.get(origin, params=params)
#         self.assertEqual(resp.status_code, 404)

#         # claim_check doesnt exist
#         params = {"username": username, "claim_check": claim_check_non_existent}
#         resp = requests.get(origin, params=params)
#         self.assertEqual(resp.status_code, 404)



# if __name__ == "__main__":
#     unittest.main()