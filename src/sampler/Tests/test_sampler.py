import unittest
from flask_testing import TestCase
from trainer.src.MKO import MKO
from sampler import app
from urllib import parse
import numpy as np
import json

class SamplerTests(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def format_params(self, endpoint, params):
        parsed = parse.urlparse(endpoint)
        encoded_params = parse.urlencode(params)
        parsed = parsed._replace(query=encoded_params)
        return parse.urlunparse(parsed)

    def test_sample(self):
        with open("trainer/test.mko", "r") as file:
            mko_data = file.read()

        SAMPLES = 100

        mko = MKO.from_b64str(mko_data)
        mko.load_data()
        mko.compile()
        mko.train()
        xs = mko._X_test.tolist()
        gt = mko.make_inference(xs, SAMPLES)

        params = {
            "model_mko": str(mko),
            "x": xs,
            "samples": SAMPLES
        }

        resp = self.client.post(self.format_params("/sample", params))
        self.assert200(resp)
        ys = np.array(json.loads(resp.data.decode('utf-8'))["y"])
        self.assertTrue(np.allclose(gt, ys, 20))



if __name__ == "__main__":
    unittest.main()
    