# frontend/Tests/base.py

import json
from flask_testing import TestCase
from server import app
from Tests import Config, testdata

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object(Config)
        return app

    def setUp(self):
        trainer_str = json.dumps(testdata.json_from_trainer)

    def tearDown(self):
        pass