# frontend/Tests/base.py
from flask_testing import TestCase
from resultCache import app

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app