import unittest
from src.MKO import MKO
import json

class TestMKO(unittest.TestCase):
    def test_parse(self):
        with open("trainer/test.json", "r") as file:
            json_file = json.load(file)
    
        mko = MKO(json_file)

        with open("trainer/test_out.json", "r") as file:
            expected_out = file.read()

        self.assertEqual(json.dumps(json.loads(mko._model.to_json())["config"]["layers"]), expected_out)

    def test_save_and_load(self):
        with open("trainer/test.json", "r") as file:
            json_file = json.load(file)
        
        mko = MKO(json_file)
        mko2 = MKO(json.loads(mko.get_json()))
        self.assertEqual(mko.get_json(), mko2.get_json())

if __name__ == "__main__":
    unittest.main()