import unittest
from trainer.src.MKO import MKO
import json

class TestMKO(unittest.TestCase):
    def test_parse(self):
        with open("trainer/test.mko", "r") as file:
            mko_data = file.read()

        with open("trainer/test_out.json", "r") as file:
            expected_out = file.read()
    
        mko = MKO.from_b64str(mko_data)

        # mko = MKO(json_data)
        # print(mko._get_json())

        # with open("trainer/test.mko", "w") as file:
        #     file.write(mko.get_b64())

        # print(mko.get_b64())
        self.assertEqual(json.dumps(json.loads(mko._model.to_json())["config"]["layers"]), expected_out)

    def test_save_and_load(self):
        with open("trainer/test.mko", "r") as file:
            mko_data = file.read()
        
        mko = MKO.from_b64str(mko_data)
        mko2 = MKO.from_b64str(mko.get_b64())
        self.assertEqual(mko.get_b64(), mko2.get_b64())


if __name__ == "__main__":
    unittest.main()