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
    ENV = 'development'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'

class TestingConfiguration(BaseConfig):
    """ Only for automated tests """
    DEBUG = True
    TESTINGCONFIG = True
    DEVELOPMENTCONFIG = False
    PRODUCTIONCONFIG = False
    ENV = 'development'
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
    ENV = 'production'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'