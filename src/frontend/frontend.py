from server import app, db
from server.models import *
from server.routes import *

@app.shell_context_processor
def make_shell_context():
    print('Registering shell context')
    return {'db': db, 'User': User, 'AuthToken': AuthToken, 'RefreshToken': RefreshToken}