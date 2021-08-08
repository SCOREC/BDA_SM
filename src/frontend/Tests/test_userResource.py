from flask import current_app, jsonify
import json

from frontend.server import app
from frontend.Tests.base import BaseTestCase
from frontend.Tests import Config
from frontend.server.models import AuthToken

from helpers import login_user, register_user, initialize_server



class UserResourceTestCase(BaseTestCase):

  # Test that flask came up correctly
  def test_user_index(self):
    with self.client:
      initialize_server(self)
      tester = app.test_client(self)
      response = tester.get('/helloWorld', content_type='html/text')
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Hello, World!' in response.data)

  # Test that login comes up correctly
  def test_user_loginpage(self):
    with self.client:
      initialize_server(self)
      tester = app.test_client(self)
      response = tester.get('/User/login', content_type='html/text')
      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Sign In' in response.data)

  def test_user_login_admin(self):
    with self.client:
      initialize_server(self)
      response = login_user(self, Config.admin_user, Config.admin_password)
      data = json.loads(response.data)
      token = data['token']
      
      (r_username, r_access_list) = AuthToken.jwt_to_access_list(token)
      self.assertEqual(Config.admin_user, r_username)
      for access in app.config.get('ADMIN_ACL'):
        self.assertIn(access, r_access_list)
      for access in r_access_list:
        self.assertIn(access, app.config.get('ADMIN_ACL'))

      self.assertFalse(AuthToken.jwt_is_expired(token))

  def test_user_get_jwt(self):
    with self.client:
      initialize_server(self)
      access_list = ['user', 'train']
      register_user(self, username="foo", password="bar", access_list=access_list)
      response = login_user(self, username="foo", password="bar")
      data = json.loads(response.data)
      token = data['token']
      
      (r_username, r_access_list) = AuthToken.jwt_to_access_list(token)
      self.assertEqual("foo", r_username)
      for access in access_list:
        self.assertIn(access, r_access_list)
      for access in r_access_list:
        self.assertIn(access, access_list)
      self.assertFalse(AuthToken.jwt_is_expired(token))


  def test_user_set_password(self):
    with self.client:
      initialize_server(self)
      register_user(self, username="foo", password="bar")
      response = login_user(self, username="foo", password="bar")
      data = json.loads(response.data)
      token = data['token']

      response = self.client.post('/User/set_password',
                                  headers={'Authorization':"Bearer {}".format(token)},
                                  data=dict(username="foo",
                                  oldpass="bar",
                                  newpass="baz"))

      self.assertEqual(response.status_code, 200)
      self.assertTrue(b'Password updated' in response.data)
      

                