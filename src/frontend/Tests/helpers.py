import json
from frontend.Tests import Config


def initialize_server(self):
  return self.client.post('/Admin/Init',
    data=dict(server_secret=Config.SERVER_SECRET,
    username=Config.admin_user, 
    password=Config.admin_password),
    follow_redirects=True
  )

def login_user(self, username, password):
  data = dict(username=username, password=password)
  return self.client.post('/User/getToken',
                          data=dict(username=username,
                          password=password))

def register_user(self, username, password, access_list=['user']):
  resp = login_user(self, Config.admin_user, Config.admin_password)
  data = json.loads(resp.data)
  token = data['token']

  return self.client.post('/Admin/create_user',
                          headers={'Authorization': "Bearer {}".format(token)},
                          data=dict(username=username, password=password, access_list=access_list))