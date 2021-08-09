from flask import render_template, Response

from server.wrappers import initialized
from server import app
from server.forms import LoginForm
from server.models import User, AuthToken, RefreshToken

@app.route('/helloWorld')
@initialized(True)
def index():
    return Response("Hello, World!", 200)



