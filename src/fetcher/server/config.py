""" Flask configurations """

from os import environ, path
basedir = path.abspath(path.dirname(__file__))

class BaseConfig(object):
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENTCONFIG = True
    TESTINGCONFIG = False
    PRODUCTIONCONFIG = False
    FLASK_ENV = 'development'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'

class TestingConfiguration(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTINGCONFIG = True
    DEVELOPMENTCONFIG = False
    PRODUCTIONCONFIG = False
    FLASK_ENV = 'testing'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'

class ProductionConfiguration(BaseConfig):
    """Production configuration"""
    DEBUG = False
    TESTINGCONFIG = False
    DEVELOPMENTCONFIG = False
    PRODUCTIONCONFIG = True
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'