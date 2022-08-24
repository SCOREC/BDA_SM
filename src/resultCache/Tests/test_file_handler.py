import unittest
from server.file_daemon import FileHandler
from server.config import TestingConfiguration as config
from Tests.helpers import get_test_set, shut_down_file_handler
from server.claim_check import ClaimCheck
import json
import time


shut_down_file_handler()
class TestFileHandler(unittest.TestCase):

    @staticmethod
    def setUpModule():
        shut_down_file_handler()

    def tearDown(self):
        shut_down_file_handler()

    def test_basic_store_and_retrieve(self):
        fh = FileHandler(config.MIN_EXPIRY_TIME, config.MAX_EXPIRY_TIME, config.RATE_AVERAGE_WINDOW, config.DIRECTORY)
        username = "user"
        claim_check = ClaimCheck(username)
        cc = claim_check.shortname
        str_data = "test_data\ntesttest"
        fh.put(username, cc, 0, str_data)
        out_data = json.loads(fh.get(username, cc))['contents']
        self.assertEqual(str_data, out_data)
        fh.end()
        fh.delete_all(True)

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

    def get_fh(self, fh, user, cc, should_delete=True):
        c = fh.get(user, cc, should_delete)
        if len(c) == 0:
            return c

        return json.loads(c)['contents']

    def check_eq(self, fh, usernames, ccs, expected, single_expectation=False, should_delete=True) -> list:
        cases = []
        
        for user in usernames:
                for cc in ccs:
                    if single_expectation:
                        cases.append((expected, self.get_fh(fh, user, cc, should_delete) ))
                    else:
                        cases.append((expected[user][cc], self.get_fh(fh, user, cc, should_delete)))
        return cases

    def test_large_volume(self):
        fh = FileHandler(config.MIN_EXPIRY_TIME, config.MAX_EXPIRY_TIME, config.RATE_AVERAGE_WINDOW, config.DIRECTORY)

        usernames, ccs, data = get_test_set()

        try:
            expected = self.put_data_and_save(fh, usernames, ccs, data)
            cases = self.check_eq(fh, usernames, ccs, expected)
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
        fh = FileHandler(config.MIN_EXPIRY_TIME, config.MAX_EXPIRY_TIME, config.RATE_AVERAGE_WINDOW, config.DIRECTORY)

        usernames, ccs, data = get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        time.sleep(2 * config.MIN_EXPIRY_TIME)

        cases = self.check_eq(fh, usernames, ccs, None, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)


    def test_multi_session_purge_test(self):
        fh = FileHandler(config.MIN_EXPIRY_TIME, config.MAX_EXPIRY_TIME, config.RATE_AVERAGE_WINDOW, config.DIRECTORY)

        usernames, ccs, data = get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        fh.end()

        fh = FileHandler(config.MIN_EXPIRY_TIME, config.MAX_EXPIRY_TIME, config.RATE_AVERAGE_WINDOW, config.DIRECTORY)

        time.sleep(2 * config.MIN_EXPIRY_TIME)

        cases = self.check_eq(fh, usernames, ccs, None, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)
                

if __name__ == "__main__":
    unittest.main()
    