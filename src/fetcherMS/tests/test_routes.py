# The fetcher test should not make any real API calls
# similar to test_fixtures.py

import pytest
import requests
from flask import Flask
import json

from fetcher import configure_app

@pytest.fixture(autouse=True)
def trainer_json():
    json_from_trainer = {
        "auth_json" : {"authenticator": "abolajiDemo",
                    "password": "memphis",
                    "name": "Dami06",
                    "role": "rpi_graphql",
                    "url": "https://rpi.cesmii.net/graphql"
                    },
       "query_json" : {"tag_ids": ["917","907","909"],
                    "start_time": "2021-00-23T20:51:40.071032+00:00",
                    "end_time": "now",
                    "max_samples": 0
        }
    }
    return json_from_trainer

# def test_fetcher_auth(trainer_json):

# def test_get_time_series():
#     response = requests.get("")

def test_base_route():
    app = Flask(__name__)   # tests.test_routes
    configure_app(app)
    client = app.test_client()
    url = '/fetcher_home'

    response = client.get(url)
    print(response.get_data())
    assert b'This is fetcher home!' in response.get_data()