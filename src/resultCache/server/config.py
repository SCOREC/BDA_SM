import os

class Constants:
    one_day_seconds = 86400

class BaseConfig(object):
    MAX_EXPIRY_TIME = 0
    MIN_EXPIRY_TIME = 0
    DIRECTORY = ""
    RATE_AVERAGE_WINDOW = 0
    JWT_SALT = ""
    JWT_ALGORITHM = "HS256"

class TestingConfiguration(BaseConfig):
    """ Testing Configuration"""
    DEBUG =  True
    TESTCONFIG = True
    ENV = 'development'

    MAX_EXPIRY_TIME = Constants.one_day_seconds
    MIN_EXPIRY_TIME = 300

    DIRECTORY = "/tmp/result_cache"
    RATE_AVERAGE_WINDOW = 10

    STRING_LEN_TEST = 20
    NUM_USERS_TEST = 10
    NUM_CC_TEST = 14
    NUM_CHARACTERS_DATA_TEST = 50
    NUM_DATA_FILES = NUM_USERS_TEST * NUM_CC_TEST

class ProductionConfiguration(BaseConfig):
    """ Production Configuration (unwise) """
    DEBUG = False
    TESTCONFIG = True
    ENV = 'Production'

    MAX_EXPIRY_TIME = Constants.one_day_seconds
    MIN_EXPIRY_TIME = 300 # seconds
    DIRECTORY = "/tmp/result_cache"
    RATE_AVERAGE_WINDOW = 1