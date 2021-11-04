import unittest
from src.MKO import MKO
import json

class TestMKO(unittest.TestCase):
    def test_parse(self):
        with open("test.json", "r") as file:
            json_file = json.load(file)
    
        mko = MKO(json_file)

        with open("test_out.json", "r") as file:
            expected_out = file.read()

        self.assertEqual(mko._model.to_json(), expected_out)

if __name__ == "__main__":
    unittest.main()