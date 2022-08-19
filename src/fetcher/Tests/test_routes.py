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


  def test_validateAttributeById(self):
    url = '/api/validateAttributeById'
    with self.client:
      attribute = testdata.attribute1
      query_json = json.dumps(
        {
          "url": testdata.smip_auth['url'],
          "smip_token": self.smip_token,
          "attrib_id": attribute['attrib_id']
        }
      )
      response = self.client.get(url, query_string={'query':query_json})
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b"Successfully validated attribute id" in response.get_data())

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


  def test_rawDataById(self):
    url = '/api/rawDataById'
    with self.client:
      attribute = testdata.attribute1
      query_json = json.dumps(
        {
          "url": testdata.smip_auth['url'],
          "smip_token": self.smip_token,
          "attrib_id": attribute['attrib_id']
        }
      )
      response = self.client.get(url, query_string={'query':query_json})
      self.assertEqual(response.content_type, 'text/html; charset=utf-8')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(attribute['result'], response.get_data())

  def test_timeseriesById(self):
    url = '/api/timeseriesById'
    with self.client:
      attribute = testdata.attribute1
      query_json = json.dumps(
        {
          "url": testdata.smip_auth['url'],
          "smip_token": self.smip_token,
          "attrib_id": attribute['attrib_id']
        }
      )
      response = self.client.get(url, query_string={'query':query_json})
      self.assertEqual(response.content_type, 'text/html; charset=utf-8')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(attribute['result'], response.get_data())