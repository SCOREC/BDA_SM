from flask import Blueprint, Response
from flask import render_template, jsonify
from flask import request

from frontend.server.errors import AuthenticationError
from frontend.server.wrappers import require_access, initialized
from frontend.server.models import User, AuthToken, RefreshToken

from .forms import LoginForm

UserResource = Blueprint('User', __name__, url_prefix='/User', template_folder='templates')


@UserResource.route('/login')
@initialized(True)
def login():
    form = LoginForm()
    return render_template('User/login.html', title='Sign in', form=form)

@UserResource.route('/logout')
@initialized(True)
@require_access('user')
def logout():
  pass
  return "<b>logout</b>"


@UserResource.route('/set_password', methods=['POST'])
@initialized(True)
@require_access('user')
def set_password():
  (bearer, token) = request.headers.get('Authorization').split()
  assert(bearer == "Bearer")
  try:
    (r_username, access_list) = AuthToken.jwt_to_access_list(token)
  except AuthenticationError:
    return Response("Authorization failed", 500)

  username = request.values.get('username')
  oldpass = request.values.get('oldpass')
  newpass = request.values.get('newpass')

  if r_username != username:
    print("User {} cannot change password for user {}.".format(r_username, username))
    return Response("User {} cannot change password for user {}.".format(r_username, username), 502)
  
  user = User.query.filter_by(username=r_username).first()
  if user is None:
    print("Authorization failed")
    return Response("Authorization failed", 500)

  if not user.check_password(oldpass):
    print("Old password does not match")
    return Response("Old password does not match", 501)

  user.set_password(newpass)
  return Response("Password updated", 200)

### API routes below ###

@UserResource.route('/getToken', methods=['POST'])
@initialized(True)
def getToken():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
          print("Failed to look up {} with password {}".format(username, password))
          raise ValueError
        auth_token = AuthToken(user=user, password=password)
        refresh_token = RefreshToken(user)
    except ValueError as err:
        print("error: {}".format(err))
        return Response("Unavailable", status=404)


    response = jsonify({"token":auth_token.payload, "expiration_date":auth_token.expiration_date})
    response.set_cookie(key='refresh_token', value=refresh_token.payload, httponly=True)
    return response

    
@UserResource.route('/refreshToken', methods=['POST', 'GET'])
@initialized(True)
@require_access('user')
def refreshToken():
    refresh_token_key = request.cookies.get('refresh_token')

    try:
        refresh_token = RefreshToken.query.filter_by(payload=refresh_token_key).first()
        print("refreshtoken: ", refresh_token)
        user = User.query.get(refresh_token.user_id)
        print("user", user)
        auth_token = AuthToken(user, refresh_token=refresh_token)
        print("auth_token", auth_token)
    except:
        return Response("Unavailable", status=404)
    token =  auth_token.payload


    response = jsonify({"token":auth_token.payload, "expiration_date":auth_token.expiration_date})
    response.status_code=201
    response.set_cookie('refresh_token', refresh_token.payload, httponly=True)
    return response
    