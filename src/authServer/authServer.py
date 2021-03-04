from app import app, db
from app.models import User, AuthToken, RefreshToken

@app.shell_context_processor
def make_shell_context():
    print('registering')
    return {'db': db, 'User': User, 'AuthToken': AuthToken, 'RefreshToken': RefreshToken}