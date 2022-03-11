from os import getenv
from threading import get_native_id
from server import app, db
from server.models import *
from server.routes import *

@app.shell_context_processor
def make_shell_context():
    print('Registering shell context')
    return {'db': db, 'User': User, 'AuthToken': AuthToken, 'RefreshToken': RefreshToken}

if __name__ == '__main__':
    app.run(
        host=getenv('IP', '0.0.0.0'),
        port=getenv('FRONTEND_PORT', 8000),
        debug=getenv('FRONTEND_DEBUG', False),
    )