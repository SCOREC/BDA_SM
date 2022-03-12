from functools import wraps

from flask import Response
from server.models import AuthToken
from flask import request, redirect
from server.errors import AuthenticationError
from server import app

def require_access(access):
  def inner_function(f):
    @wraps(f)
    def access_checker(*args, **kwargs):
      if not request.headers.get('Authorization'):
        return redirect("/User/login", code=302)

      try:
        header = request.headers.get('Authorization')
        (_, token) = header.split()
      except:
        return Response("Malformed header", 400)

      if token is None:
        return Response("Access denied", 401)

      try:
        (username, access_list) = AuthToken.jwt_to_access_list(token)
      except AuthenticationError:
        return Response("Access denied", 403)

      if access not in access_list:
        return Response("Access denied", 403)
      else:
        return f(*args, **kwargs)

    return access_checker
      
  return inner_function

def initialized(state):
  def inner_function(f):
    @wraps(f)
    def initialization_checker(*args, **kwargs):
      if state == app.config['INITIALIZED']:
        return f(*args, **kwargs)
      else:
        return Response("Server not found", 409)

    return initialization_checker
      
  return inner_function