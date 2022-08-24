# frontend/Tests/base.py
from flask_testing import TestCase
from server import app
from server.config import TestingConfiguration as Config
import Tests.helpers

class BaseTestCase(TestCase):
  def create_app(self):
    app.config.from_object(Config)
    app.config['TESTING'] = True
    return app

  @staticmethod
  def setUpModule():
    Tests.helpers.shut_down_file_handler()

  def setUp(self):
    Tests.helpers.bring_up_file_handler()

  def tearDown(self):
    Tests.helpers.shut_down_file_handler()