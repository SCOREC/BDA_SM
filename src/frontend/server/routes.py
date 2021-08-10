from flask import render_template, Response
from flask import send_from_directory, abort

from server.wrappers import initialized
from server import app
from server.forms import LoginForm
from server.models import User, AuthToken, RefreshToken

@app.route('/helloWorld')
@initialized(True)
def index():
    return Response("Hello, World!", 200)

@app.route('/get-csv/<csv_id>')
def send_csv(csv_id):
  filename = f"{csv_id}.csv"
  try:
    return send_from_directory("/tmp/csvfiles", filename=filename, as_attachment=True)
  except FileNotFoundError:
    abort(404)






