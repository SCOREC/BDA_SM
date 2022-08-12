import json
from flask import Flask

from server import app
from Tests.base import BaseTestCase
from testdata import trainer_str as trainer_str

class HeartbeatTestCase(BaseTestCase):
  """Various 'am i alive' type tests"""

  def test_client(self):
    url = '/api/echo'
    with self.client:
      response = self.client.get(url,query_string={'query':trainer_str})
      self.assertEqual(response.status_code, 200)

  def test_home_route(self):
    url = '/fetcher_home'
    with self.client:
      response = self.client.get(url)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'This is fetcher home!' in response.get_data())

class ContentTestCase(BaseTestCase):
  """ Actual information from the CESMII server"""

  def test_gettimeseries(self):
    url = '/api/gettimeseries'
    with self.client:
      response = self.client.get(url, query_string={'query':trainer_str})
      self.assertEqual(response.content_type, 'application/json') 
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'ts' or b'data' in response.get_data())
      self.assertTrue(b'215' in response.get_data())


  def test_getEquipmentData(self):
    url = '/api/getEquipmentData'
    with self.client:
      response = self.client.get(url, query_string={'query':trainer_str})
      self.assertEqual(response.status_code, 200)

  def test_getEquipmentTypes(self):
    url = '/api/getEquipmentTypes'
    with self.client:
      response = self.client.get(url, query_string={'query':trainer_str})
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'data' in response.get_data())

  def test_getEquipment(self):
    url = '/api/getEquipment'
    with self.client:
      response = self.client.get(url, query_string={'query':trainer_str})
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'data' in response.get_data())


def test_fetcher_no_auth(self):
    url = '/api/gettimeseries'
    with self.client:
      no_auth_json = json.loads(trainer_str)
      no_auth_json['auth_json'] = {}
      no_auth_str = json.dumps(no_auth_json)

      response = self.client.get(url, query_string={'query':no_auth_str})
      self.assertTrue(b'Bad Request' in response.get_data())
      self.assertEqual(response.status_code, 400)

def test_fetcher_no_query(self):
    url = '/api/gettimeseries'
    with self.client:
      no_query_json = json.loads(trainer_str)
      no_query_json['query_json'] = {}
      no_query_str = json.dumps(no_query_json)

      response = self.client.get(url, query_string={'query':no_query_str})
      self.assertTrue(b'Bad Request' in response.get_data())
      self.assertEqual(response.status_code, 400)