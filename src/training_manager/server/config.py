
from os import environ, path
import sys
basedir = path.abspath(path.dirname(__file__))

""" External services configurations """
class ExternalsConfig(object):
  EXECUTABLE_WORKING_DIRECTORY = environ.get("TRAINER_WORKING_DIRECTORY", "./trainer")
  PYTHON_EXECUTABLE = sys.executable
  EXECUTABLE_NAME = [PYTHON_EXECUTABLE,  "trainer.py"]
  RESULTS_CACHE_PORT = environ.get('RESULTS_CACHE_PORT', 5002)
  RESULTS_CACHE_BASE_URL = environ.get('RESULTS_CACHE_BASE_URL',
    'http://localhost:{}'.format(RESULTS_CACHE_PORT))
  FETCHER_PORT = environ.get('FETCHER_BASE_PORT', 5004)
  FETCHER_URL = environ.get('FETCHER_BASE_URL',
    'http://localhost:{}'.format(FETCHER_PORT))


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