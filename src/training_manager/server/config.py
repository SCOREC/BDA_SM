
from os import environ, path
basedir = path.abspath(path.dirname(__file__))

""" Trainer configurations """
class TrainerConfig(object):
  EXECUTABLE_PATH = "python -m trainer.src.trainer".split(" ")
  RESULTS_CACHE_PORT = environ.get('RESULTS_CACHE_PORT', 5001)
  RESULTS_CACHE_URI = environ.get('RESULTS_CACHE_URL',
    'http://localhost:{}'.format(RESULTS_CACHE_PORT))


""" Flask configurations """
class BaseConfig(object):
  FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
  FLASK_APP = environ.get('FLASK_APP')

class DevelopmentConfig(BaseConfig):
  """Development configuration"""
  DEBUG = True
  DEVELOPMENTCONFIG = True
  TESTINGCONFIG = False
  PRODUCTIONCONFIG = False
  FLASK_ENV = 'development'
  FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
  FLASK_APP = environ.get('FLASK_APP')

class TestingConfiguration(BaseConfig):
  """Testing configuration"""
  DEBUG = True
  TESTINGCONFIG = True
  DEVELOPMENTCONFIG = False
  PRODUCTIONCONFIG = False
  FLASK_ENV = 'testing'
  FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
  FLASK_APP = environ.get('FLASK_APP')

class ProductionConfiguration(BaseConfig):
  """Production configuration"""
  DEBUG = False
  TESTINGCONFIG = False
  DEVELOPMENTCONFIG = False
  PRODUCTIONCONFIG = True
  FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
  FLASK_APP = environ.get('FLASK_APP')