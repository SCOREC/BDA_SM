from flask import current_app, jsonify
import json
from server import app
from Tests.base import BaseTestCase
from Tests import Config

from helpers import login_user, register_user, initialize_server


class AdminResourceTestCase(BaseTestCase):

  #Test that admin initialization works
  def test_admin_init(self):
    with self.client:
      response = self.client.post('/Admin/Init',
        data=dict(server_secret="NotTheRealSecret",
        username=Config.admin_user, 
        password=Config.admin_password),
        follow_redirects=True
      )
      self.assertEqual(response.status_code, 501)
      self.assertTrue(b'Failed to initialize' in response.data)
      self.assertFalse(app.config.get('INITIALIZED'))

      response = self.client.post('/Admin/Init',
        data=dict(server_secret=app.config.get('SERVER_SECRET'),
        username=Config.admin_user, 
        password=Config.admin_password),
        follow_redirects=True
      )
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Server is now initialized!' in response.data)
      self.assertTrue(app.config.get('INITIALIZED'))

  def test_admin_register_user(self):
    with self.client:
      initialize_server(self)
      response = register_user(self,"foo", "bar")
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'User "foo" created.' in response.data)

      response = register_user(self,"foo", "baz")
      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'Username already taken.' in response.data)

      response = register_user(self,"baz", "bar", access_list=['thud'])
      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'not a valid access level' in response.data)


  def test_admin_set_password(self):
    with self.client:
      initialize_server(self)
      register_user(self, username="foo", password="bar")
      response = login_user(self, username=Config.admin_user, password=Config.admin_password)
      data = json.loads(response.data)
      token = data['token']

      response = self.client.post('/Admin/set_password',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="foo",
                                  password="different"))

      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Updated password for foo.' in response.data)

      response = self.client.post('/Admin/set_password',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="thud",
                                  password="different"))

      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'No such user' in response.data)

  def test_admin_set_access_list(self):
    with self.client:
      initialize_server(self)
      register_user(self, username="foo", password="bar")
      response = login_user(self, username=Config.admin_user, password=Config.admin_password)
      data = json.loads(response.data)
      token = data['token']

      response = self.client.post('/Admin/set_access_list',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="foo",
                                  access_list=Config.ADMIN_ACL))

      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Updated access_list for foo to' in response.data)

      response = self.client.post('/Admin/set_access_list',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="bar",
                                  access_list=['thud']))

      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'thud not a valid access level' in response.data)

      response = self.client.post('/Admin/set_access_list',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="thud",
                                  access_list=Config.ADMIN_ACL))

      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'No such user as thud' in response.data)

  def test_admin_delete_user(self):
    with self.client:
      initialize_server(self)
      register_user(self, username="foo", password="bar")
      response = login_user(self, username=Config.admin_user, password=Config.admin_password)
      data = json.loads(response.data)
      token = data['token']

      response = self.client.post('/Admin/delete_user',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="foo"))

      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Deleted user foo.' in response.data)

      response = self.client.post('/Admin/delete_user',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="foo"))

      self.assertEqual(response.status_code, 500)
      self.assertTrue(b'No such user' in response.data)