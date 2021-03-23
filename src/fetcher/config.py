""" Flask configurations """

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir,'.env'))

class Config:
    """ Flask variables """

    TESTING = True
    DEBUG = True
    FLASK_ENV = 'development'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    FLASK_APP = environ.get('FLASK_APP')
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
