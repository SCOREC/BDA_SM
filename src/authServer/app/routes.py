from flask import render_template
from flask import Response, request, jsonify

from app import app
from app.forms import LoginForm
from app.models import User, AuthToken, RefreshToken

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign in', form=form)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/getToken', methods=['POST','GET'])
def getToken():
    username = request.values.get('username')
    password = request.values.get('password')
    print("username: {}, password: {}".format(username,password))

    try:
        user = User.query.filter_by(username=username).first()
        print("pass 1")
        auth_token = AuthToken(user=user, access_list=user.access_list, password=password)
        print(auth_token)
        refresh_token = RefreshToken(user, user.access_list)
        print("pass 3")
    except ValueError as err:
        print("error: {}".format(err))
        return Response("Unavailable", status=404)


    response = jsonify({"token":auth_token.payload, "expiration_date":auth_token.expiration_date})
    #response = Response(response=({'token':auth_token.payload, 'expiration_date:':auth_token.expiration_date}),  status=200)
    print(response)
    response.set_cookie(key='refresh_token', value=refresh_token.payload, httponly=True)
    return response
    
@app.route('/refreshToken', methods=['POST', 'GET'])
def refreshToken():
    refresh_token_key = request.cookies.get('refresh_token')
    print("RF from cookie: {}".format(refresh_token_key))

    try:
        refresh_token = RefreshToken.query.filter_by(payload=refresh_token_key).first()
        print("RF: {}".format(refresh_token))
        user = User.query.get(refresh_token.user_id)
        print("user: {}".format(user))
        auth_token = AuthToken(user, refresh_token=refresh_token)
        print("AT: {}".format(auth_token))
    except:
        return Response("Unavailable", status=404)
    token =  auth_token.payload


    response = jsonify({"token":auth_token.payload, "expiration_date":auth_token.expiration_date})
    response.status_code=201
    response.set_cookie('refresh_token', refresh_token.payload, httponly=True)
    return response
    