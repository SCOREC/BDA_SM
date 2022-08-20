from flask.wrappers import Response
from server import app

@app.route('/helloWorld')
def index():
    return Response("Hello World!", 200)