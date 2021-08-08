from functools import wraps

from flask.wrappers import Response
from frontend.server.models import AuthToken
from flask import request, redirect
from frontend.server.errors import AuthenticationError
from frontend.server import app

def require_access(access):
  def inner_function(f):
    @wraps(f)
    def access_checker(*args, **kwargs):
      if not request.headers.get('Authorization'):
        return redirect("/User/login", code=302)

      (bearer, token) = request.headers.get('Authorization').split()

      (username, access_list) = AuthToken.jwt_to_access_list(token)
      if access in access_list:
        return f(*args, **kwargs)

      raise AuthenticationError("User {} does not have {} access".format(username, access)) 

    return access_checker
      
  return inner_function

def initialized(state):
  def inner_function(f):
    @wraps(f)
    def initialization_checker(*args, **kwargs):
      if state == app.config['INITIALIZED']:
        return f(*args, **kwargs)
      else:
        print("rejecting as wrong state. State is {}".format(app.config.get('INITIALIZED')))
        return Response("foo", 404)

    return initialization_checker
      
  return inner_function