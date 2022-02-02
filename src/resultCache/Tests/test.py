import unittest
from resultCache.file_daemon import FileHandler
from resultCache.config import TestConfig as config
from resultCache.Tests.helpers import get_test_set
import json
import time


class TestFileHandler(unittest.TestCase):
    def test_basic_store_and_retrieve(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)
        username = "user"
        cc = "test_str"
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

    def get_fh(self, fh, user, cc):
        c = fh.get(user, cc)
        if c == None:
            return c

        return json.loads(c)['contents']

    def check_eq(self, fh, usernames, ccs, expected, single_expectation=False) -> list:
        cases = []
        
        for user in usernames:
                for cc in ccs:
                    if single_expectation:
                        cases.append((expected, self.get_fh(fh, user,cc) ))
                    else:
                        cases.append((expected[user][cc], self.get_fh(fh, user, cc)))
        return cases

    def test_large_volume(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

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
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        usernames, ccs, data = get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        time.sleep(2 * config.min_expiry_time)

        cases = self.check_eq(fh, usernames, ccs, None, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)


    def test_multi_session_purge_test(self):
        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        usernames, ccs, data = get_test_set()
        datum = data[0]

        self.put_datum(fh, usernames, ccs, datum)

        fh.end()

        fh = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)

        time.sleep(2 * config.min_expiry_time)

        cases = self.check_eq(fh, usernames, ccs, None, single_expectation=True)

        fh.end()
        fh.delete_all(True)

        for case in cases:
            self.assertEqual(*case)
                

if __name__ == "__main__":
    unittest.main()