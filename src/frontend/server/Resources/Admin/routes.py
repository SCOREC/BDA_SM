from flask import Blueprint
from flask import render_template
from flask import request, jsonify, abort
from flask.wrappers import Response

from server import app, db
from server.errors import AuthenticationError
from server.wrappers import require_access, initialized
from server.models import User, AuthToken, RefreshToken

AdminResource = Blueprint('Admin', __name__, url_prefix='/Admin')

@AdminResource.route('/Init', methods=['GET','POST'])
@initialized(False)
def admin_server_init():
  server_secret = request.values.get('server_secret')
  username = request.values.get('username')
  password = request.values.get('password')

  User.query.delete()
  db.session.commit()
  try:
    if server_secret == app.config.get('SERVER_SECRET'):
      u = User(username=username,
               password=password,
               access_list=app.config.get('ADMIN_ACL'))

      db.session.add(u)
      db.session.commit()
    else:
      return Response("Failed to initialize", 501)
  except Exception as err:
    return Response("Failed to initialize {}".format(err), 500)
  
  app.config['INITIALIZED'] = True
  return Response("Server is now initialized!", 200)

@AdminResource.route('/create_user', methods=['POST'])
@initialized(True)
@require_access('admin')
def admin_create_user():
    
  username = request.form.get('username')
  password = request.form.get('password')
  access_list = request.form.getlist('access_list')
  email = request.form.get('email')
  
  olduser = User.query.filter_by(username=username).first()
  if olduser is not None:
    return Response("Username already taken.", 500)

  for access in access_list:
    if access not in app.config.get('ADMIN_ACL'):
      return Response("{} not a valid access level".format(access),500)

  u = User(username=username,
          password=password,
          email=email,
          access_list=access_list)
  
  db.session.add(u)
  db.session.commit()

  return Response('User "{}" created.'.format(username), 200)

@AdminResource.route('/delete_user', methods=['POST'])
@initialized(True)
@require_access('admin')
def delete_user():
  username = request.values.get('username')
  u = User.query.filter_by(username=username).first()

  if u is None:
    return Response("No such user", 500)
  else:
    u.delete()
    db.session.commit()
  return Response("Deleted user {}.".format(username), 200)

@AdminResource.route('/set_password', methods=['POST'])
@initialized(True)
@require_access('admin')
def admin_set_password():
  username = request.values.get('username')
  password = request.values.get('password')
  u = User.query.filter_by(username=username).first()

  if u is None:
    return Response("No such user", 500)
  else:
    u.set_password(password)
  db.session.commit()
  return Response("Updated password for {}.".format(username), 200)


@AdminResource.route('/set_access_list', methods=['POST'])
@initialized(True)
@require_access('admin')
def admin_set_access_list():
  username = request.values.get('username')
  password = request.values.get('password')
  access_list = request.form.getlist('access_list')

  for access in access_list:
    if access not in app.config.get('ADMIN_ACL'):
      return Response("{} not a valid access level".format(access),500)

  u = User.query.filter_by(username=username).first()

  if u is None:
    return Response("No such user as {}".format(username), 500)
  else:
    u.set_access_list(access_list)
  db.session.commit()
  return Response("Updated access_list for {} to {}.".format(username, access_list), 200)