from flask import current_app, jsonify
import json
from frontend.server import app
from frontend.Tests.base import BaseTestCase
from frontend.Tests import Config
from frontend.server.models import AuthToken

from helpers import login_user, register_user, initialize_server


class LoggingResourceTestCase(BaseTestCase):

  #Test that admin initialization works
  def test_logging_viewall(self):
    with self.client:
      initialize_server(self)
      response = register_user(self,"foo", "bar",access_list=["logs"])
      response = login_user(self, username="foo", password="bar")
      data = json.loads(response.data)
      token = data['token']
      response = self.client.post('/Logging/viewall',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  follow_redirects=True
                                  )
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Created user' in response.data)
