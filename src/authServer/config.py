import os
basedir = os.path.abspath(os.path.dirname(__file__))
JWT_LIFETIME = int(os.environ.get('JWTLIFETIME') or  1800) # Lifetime in seconds
JWT_SECRET = os.environ.get('JWTSECRET') 
JWT_ALGORITHM = 'HS256'


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'authServer.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or  'some-entropy'
