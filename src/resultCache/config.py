import os
from typing import Mapping

class Constants:
    one_day_seconds = 86400

class Config:
    max_expiry_time = None
    min_expiry_time = None
    directory = None

class ProductionConfig(Config):
    max_expiry_time = Constants.one_day_seconds
    min_expiry_time = 300 # seconds
    directory = "."

class TestConfig(Config):
    max_expiry_time = Constants.one_day_seconds
    min_expiry_time = 4

    string_len_test = 20
    num_users_test = 20
    num_cc_test = 30
    num_characters_data_test = 500
    num_data_files = num_users_test * num_cc_test
    directory = "src/resultCache/.data"

def _get_config() -> Config:
    version = os.environ.get("ENV", "production")

    mapping: Mapping[str, Config] = {
        "production": ProductionConfig(),
        "test": TestConfig(),
    }

    config = mapping[version]

    config.directory = os.environ.get("DATA_DIR", config.directory)
    
    return config

config = _get_config()


