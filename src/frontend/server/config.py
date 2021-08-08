import os
basedir = os.path.abspath(os.path.dirname(__file__))
database_name = 'frontend.db'

class BaseConfig(object):
  # ...

  SECRET_KEY = os.getenv('SECRET_KEY', 'some-entropy')
  INITIALIZED = False  # Global indicating whether server has been initialized after initial startup
  BASECONFIG = True
  DEBUG = False
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  JWT_LIFETIME = int(os.environ.get('JWTLIFETIME') or  1800) # Lifetime in seconds
  JWT_ALGORITHM = 'HS256'
  JWT_SECRET = os.environ.get('JWTSECRET') or SECRET_KEY
  ADMIN_ACL = ['user', 'admin', 'train', 'infer', 'logging']

class DevelopmentConfig(BaseConfig):
  """Development configuration"""
  DEBUG = True 
  DEVELOPMENTCONFIG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, database_name)
  SERVER_SECRET = '0123'
  
class TestingConfiguration(BaseConfig):
  DEBUG = True
  TESTING = True
  TESTINGCONFIG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, database_name) 
  SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI + "_test"
  SERVER_SECRET = '0123'
  admin_user = "admin"
  admin_password = "adpass"
  
class ProductionConfiguration(BaseConfig):
  """For deployment"""
  DEBUG = False
  PRODUCTIONCONFIG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, database_name)
  JWT_SECRET = os.environ.get('JWT_SECRET') or BaseConfig.SECRET_KEY
  SERVER_SECRET = os.environ.get('server_secret')