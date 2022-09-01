import os
basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.join(basedir, "databases")
database_name = 'frontend.db'
jwt_salt = str(os.urandom(24))

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
  JWT_SECRET = JWT_SECRET + jwt_salt
  ADMIN_ACL = ['user', 'admin', 'train', 'infer', 'analyze', 'logs']
  TRAINING_MANAGER_BASE_URL = None
  INFERENCE_MANAGER_BASE_URL = None
  RESULT_CACHE_BASE_URL = None

  
class DevelopmentConfiguration(BaseConfig):
  DEBUG = True
  TESTING = True
  TESTINGCONFIG = True
  PRODUCTIONCONFIG = False
  ENV = 'development'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, database_name) 
  _index = SQLALCHEMY_DATABASE_URI.find(".db")
  SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI[:_index] + "_test" \
                            + SQLALCHEMY_DATABASE_URI[_index:]
  _index = SQLALCHEMY_DATABASE_URI.find(".db")
  SQLALCHEMY_BINDS = {'log': SQLALCHEMY_DATABASE_URI[:_index]
                      + '_log' + SQLALCHEMY_DATABASE_URI[_index:]}
  SERVER_SECRET = os.environ.get('server_secret', '0123')
  TRAINING_MANAGER_BASE_URL = os.environ.get("TRAINING_MANAGER_BASE_URL",'http://localhost:5001/')
  RESULT_CACHE_BASE_URL = os.environ.get("RESULT_CACHE_BASE_URL",'http://localhost:5002/')
  INFERENCE_MANAGER_BASE_URL = os.environ.get("INFERENCE_MANAGER_BASE_URL",'http://localhost:5003/')
  
class TestingConfiguration(BaseConfig):
  """ Automated testing only """
  DEBUG = True
  TESTING = True
  TESTINGCONFIG = True
  PRODUCTIONCONFIG = False
  ENV = 'testing'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, database_name) 
  _index = SQLALCHEMY_DATABASE_URI.find(".db")
  SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI[:_index] + "_test" \
                            + SQLALCHEMY_DATABASE_URI[_index:]
  _index = SQLALCHEMY_DATABASE_URI.find(".db")
  SQLALCHEMY_BINDS = {'log': SQLALCHEMY_DATABASE_URI[:_index]
                      + '_log' + SQLALCHEMY_DATABASE_URI[_index:]}
  SERVER_SECRET = '0123'
  admin_user = "admin"
  admin_password = "adpass"
  TRAINING_MANAGER_BASE_URL = os.environ.get("TRAINING_MANAGER_BASE_URL",'http://localhost:5001/')
  RESULT_CACHE_BASE_URL = os.environ.get("RESULT_CACHE_BASE_URL",'http://localhost:5002/')
  INFERENCE_MANAGER_BASE_URL = os.environ.get("INFERENCE_MANAGER_BASE_URL",'http://localhost:5003/')
  
class ProductionConfiguration(BaseConfig):
  """For deployment"""
  DEBUG = False
  PRODUCTIONCONFIG = True
  ENV = 'production'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, database_name)
  SQLALCHEMY_BINDS = {'log': SQLALCHEMY_DATABASE_URI + '_log'}
  JWT_SECRET = os.environ.get('JWT_SECRET') or BaseConfig.SECRET_KEY
  JWT_SECRET = JWT_SECRET + jwt_salt
  SERVER_SECRET = os.environ.get('server_secret')