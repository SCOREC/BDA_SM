from os import getenv
from server import app

if __name__ == '__main__':
    app.run(
        host=getenv('IP', '0.0.0.0'),
        port=getenv('FRONTEND_PORT', 5000),
        debug=getenv('FRONTEND_DEBUG', False),
    )