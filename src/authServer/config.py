import os
basedir = os.path.abspath(os.path.dirname(__file__))
JWT_LIFETIME = os.environ.get('JWTLIFETIME') or  1800 # Lifetime in seconds
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'authServer.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
