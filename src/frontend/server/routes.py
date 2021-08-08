from flask import render_template, Response

from frontend.server.wrappers import initialized
from frontend.server import app
from frontend.server.forms import LoginForm
from frontend.server.models import User, AuthToken, RefreshToken

@app.route('/helloWorld')
@initialized(True)
def index():
    return Response("Hello, World!", 200)



