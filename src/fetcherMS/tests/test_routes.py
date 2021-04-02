# The fetcher test should not make any real API calls
# similar to test_fixtures.py
try:
    import pytest
    from flask import Flask
    from fetcher import configure_app, app
except Exception as e:
    print("Some modules are missing {}".format(e))

json_from_trainer = {
    "auth_json" : {"authenticator": "abolajiDemo",
                "password": "memphis",
                "name": "Dami06",
                "role": "rpi_graphql",
                "url": "https://rpi.cesmii.net/graphql"
                },
   "query_json" : {"tag_ids": ["984"],
                "start_time": "2020-01-23T20:51:40.071032+00:00",
                "end_time": "now",
                "max_samples": 0
    }
}

@pytest.fixture(autouse=True)
def mock_trainer_json():
    return json_from_trainer

def test_home_route():
    test_app = Flask(__name__)
    configure_app(test_app)
    client = test_app.test_client()
    url = '/fetcher_home'

    response = client.get(url)
    assert b'This is fetcher home!' in response.get_data()
    assert response.status_code == 200

def test_app_content():
    test_app = Flask(__name__)
    configure_app(test_app)
    client = test_app.test_client()
    url = '/api/gettimeseries'

    response = client.get(url, json=json_from_trainer)
    assert response.content_type == "application/json"
    assert response.status_code == 200

def test_fetcher_route():
    test_app = Flask(__name__)
    configure_app(test_app)
    client = test_app.test_client()
    url = '/api/gettimeseries'

    response = client.get(url, json=json_from_trainer)
    print(response.get_data())
    assert b'ts' in response.get_data()
    assert response.status_code == 200

def test_fetcher_no_auth():
    test_app = Flask(__name__)
    configure_app(test_app)
    client = test_app.test_client()
    url = '/api/gettimeseries'
    json_from_trainer['auth_json'] = {}

    response = client.get(url, json=json_from_trainer)
    assert b'error' in response.get_data()
    assert response.status_code == 500

def test_fetcher_no_query():
    test_app = Flask(__name__)
    configure_app(test_app)
    client = test_app.test_client()
    url = '/api/gettimeseries'
    json_from_trainer['query_json'] = {}

    response = client.get(url, json=json_from_trainer)
    assert b'error' in response.get_data()
    assert response.status_code == 500