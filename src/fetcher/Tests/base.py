# frontend/Tests/base.py
from flask_testing import TestCase
from server import app
from server.smip.graphQL import get_bearer_token
from Tests import Config, testdata


class BaseTestCase(TestCase):
  """Base Tests"""

  def create_app(self):
    app.config.from_object(Config)
    return app

  def setUp(self):
    smip_token = get_bearer_token(
      testdata.smip_auth["url"],
      username=testdata.smip_auth["username"],
      role=testdata.smip_auth["role"],
      password=testdata.smip_auth["password"],
    )
    self.smip_token = smip_token

  def tearDown(self):
    pass
