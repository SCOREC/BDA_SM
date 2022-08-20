# frontend/Tests/base.py
from flask_testing import TestCase
from server import app
from Tests import Config, testdata


class BaseTestCase(TestCase):
  """Base Tests"""

  def create_app(self):
    app.config.from_object(Config)
    return app

  def setUp(self):
    pass

  def tearDown(self):
    pass
