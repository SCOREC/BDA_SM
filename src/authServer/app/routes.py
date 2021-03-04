from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/getToken')
def getToken():
    return "Here is a token"