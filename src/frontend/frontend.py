from frontend.server import app, db
from frontend.server.models import *
from frontend.server.routes import *

@app.shell_context_processor
def make_shell_context():
    print('registering')
    return {'db': db, 'User': User, 'AuthToken': AuthToken, 'RefreshToken': RefreshToken}