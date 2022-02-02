# frontend/Tests/base.py
from flask_testing import TestCase
from resultCache import app
from resultCache import routes
from resultCache.config import TestConfig as config

class BaseTestCase(TestCase):
    def create_app(self):
        routes.set_config(config)
        app.config['TESTING'] = True
        return app

    def tearDownClass():
        if routes.file_handler != None:
            routes.file_handler.end()
            routes.file_handler.delete_all(True)