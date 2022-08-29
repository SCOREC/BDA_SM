import json
from flask import Flask
from Tests import testdata

from server import app
from Tests.base import BaseTestCase
import testdata
from testdata import trainer_str

class HeartbeatTestCase(BaseTestCase):
  """Various 'am i alive' type tests"""

  def test_home_route(self):
    url = '/helloWorld'
    with self.client:
      response = self.client.get(url)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Hello World!' in response.get_data())

class ContentTestCase(BaseTestCase):
  """ Actual information from the CESMII server"""

  def test_create_MKO(self):
    url = '/api/create_MKO'
    with self.client:
      query_json = json.dumps(
        {
          "username": testdata.good_username,
          "model_name": testdata.good_modelname
        }
      )
      response = self.client.post(url, query_string={'query':query_json})
      self.assertEqual(response.status_code, 200)
      token = response.get_data()
      

      query_json = json.dumps(
        {
          "url": testdata.smip_auth['url'],
          "smip_token": self.smip_token,
          "attrib_id": "9999999"
        }
      )
      response = self.client.get(url, query_string={'query':query_json})
      self.assertEqual(response.status_code, 422)
      self.assertTrue(b"No such attribute" in response.get_data())

