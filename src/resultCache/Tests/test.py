import unittest

from requests.models import DEFAULT_REDIRECT_LIMIT
from resultCache.file_daemon import FileHandler
from resultCache.config import TestConfig as config
import random
import string
import time
import requests
import subprocess

class TestFileHandler(unittest.TestCase):
    def test_basic_store_and_retrieve_str(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)
        username = "user"
        cc = "test_str"
        str_data = "test_data\ntesttest"
        fh.put(username, cc, 0, str_data)
        out_data = fh.get(username, cc, str)
        self.assertEqual(str_data, out_data)
        fh.end()
        fh.delete_all(True)

    def test_basic_store_and_retrieve_bin(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)
        username = "user"
        cc = "test_str"
        bin_data = b"test_data\ntesttest"
        fh.put(username, cc, 0, bin_data)
        out_data = fh.get(username, cc, bytes)
        self.assertEqual(bin_data, out_data)
        fh.end()
        fh.delete_all(True)

    def generate_string(self, l, n):
        strings = []
        for _ in range(n):
            gen_string = ''.join(random.choice(string.ascii_letters) for _ in range(l))
            strings.append(gen_string)
        return strings

    def get_test_set(self):
        usernames = self.generate_string(config.num_users_test, config.string_len_test)
        ccs = self.generate_string(config.num_cc_test, config.string_len_test)
        data = self.generate_string(config.num_data_files, config.num_characters_data_test)
        return usernames, ccs, data

    def put_data_and_save(self, fh, usernames, ccs, data):
        expected = {}
        datum_index = 0
        for user in usernames:
            expected[user] = {}
            for cc in ccs:
                datum = data[datum_index]
                expected[user][cc] = datum
                fh.put(user, cc, 0, datum)
        return expected

    def check_eq(self, fh, usernames, ccs, expected, type, single_expectation=False) -> list:
        cases = []
        

        for user in usernames:
                for cc in ccs:
                    if single_expectation:
                        cases.append((expected, fh.get(user, cc, type)))
                    else:
                        cases.append((expected[user][cc], fh.get(user, cc, type)))
        return cases

    def test_large_volume(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        usernames, ccs, data = self.get_test_set()

        try:
            expected = self.put_data_and_save(fh, usernames, ccs, data)
            cases = self.check_eq(fh, usernames, ccs, expected, str)
        except Exception as e:
            fh.end()
            fh.delete_all(True)
            self.fail(e.with_traceback)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(case[0], case[1])

    def put_datum(self, fh, usernames, ccs, datum):
        for user in usernames:
            for cc in ccs:
                fh.put(user, cc, 0, datum)

    def test_purge_test(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        usernames, ccs, data = self.get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        time.sleep(2 * config.min_expiry_time)

        cases = self.check_eq(fh, usernames, ccs, None, str, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)


    def test_multi_session_purge_test(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        usernames, ccs, data = self.get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        fh.end()

        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        time.sleep(2 * config.min_expiry_time)

        cases = self.check_eq(fh, usernames, ccs, None, str, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)


    def start_server(self):
        command = "cd src/resultCache && export ENV=test && export DATA_DIR=.data && ./run_server.sh".split(" ")
        # command = "ls"
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    def send_put(self, username, claim_check, generation_time, data) -> requests.Response:
        params = {"username": username, "claim_check": claim_check, "generation_time": generation_time}
        return requests.post("http://127.0.0.1:5000/store_result", data=data, params=params)

    def get_data(self, username, claim_check) -> requests.Response:
        params = {"username": username, "claim_check": claim_check}
        return requests.get("http://127.0.0.1:5000/get_result", params=params)

    def kill_server(self):
        requests.post("http://127.0.0.1:5000/close")


    def test_basic_rest_api(self):
        # proc = self.start_server()
        # time.sleep(1)
        username = "abcdefg"
        claim_check = "1234567"
        generation_time = "1"
        data = self.generate_string(config.string_len_test, 1)[0]

        self.send_put(username, claim_check, generation_time, data)

        resp = self.get_data(username, claim_check)
        # self.kill_server()
        self.assertEqual(resp.text, data)

    def put_data_rest(self, usernames, ccs, data):
        data_index = 0
        for user in usernames:
            for cc in ccs:
                datum = data[data_index]
                self.send_put(user, cc, 0, datum)
                data_index += 1

    def test_volume_api(self):
        usernames, ccs, data = self.get_test_set()
        self.put_data_rest(self, usernames, ccs, data)


                

if __name__ == "__main__":
    unittest.main()