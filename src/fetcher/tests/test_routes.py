# These fetcher tests make real API calls
# similar to test_fixtures.py
try:
    import json
    import pytest
    from flask import Flask
    from api import configure_app, app, fetcher
except Exception as e:
    print("Some modules are missing {}".format(e))

json_from_trainer = {
    "auth_json" : {"authenticator": "kaushp",
                "password": "welcome001",
                "name": "kaushp",
                "role": "rpi_ro_group",
                "url": "https://rpi.cesmii.net/graphql"
                },
   "query_json" : {"tag_ids": ["984"],
                "start_time": "2020-01-23T20:51:40.071032+00:00",
                "end_time": "now",
                "GMT_prefix_sign":"plus",
                "max_samples": 0
                },

    "get_data" : {
                    "Attribute": "Electric Potential",
                    "Equipment": "Motor"
                 }
}

@pytest.fixture(autouse=True)
def trainer_str():
    return json.dumps(json_from_trainer)

@pytest.fixture(autouse=True)
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_home_route(client):
    url = '/fetcher_home'

    response = client.get(url)
    assert b'This is fetcher home!' in response.get_data()
    assert response.status_code == 200

def test_app_content(client, trainer_str):
    url = '/api/gettimeseries'

    response = client.get(url, query_string={'query':trainer_str})
    assert response.content_type == "application/json"
    assert response.status_code == 200

def test_getTS(client, trainer_str):
    url = '/api/gettimeseries'
    response = client.get(url, query_string={'query':trainer_str})
    print(response.get_data())
    assert b'ts' or b'data' in response.get_data()
    assert b'215' in response.get_data()
    assert response.status_code == 200

# def test_getData(client, trainer_str):
#     url = '/api/getdata'
#     response = client.get(url, query_string = {'query': trainer_str})
#     print(response.get_data())
#     assert response.status_code == 200

def test_getET(client, trainer_str):
    url = '/api/getEquipmentTypes'
    response = client.get(url, query_string = {'query': trainer_str})
    print(response.get_data())
    assert b'data' in response.get_data()
    assert response.status_code == 200

def test_getEquipments(client, trainer_str):
    url = '/api/getEquipment'
    response = client.get(url, query_string = {'query': trainer_str})
    print(response.get_data())
    assert b'data' in response.get_data()
    assert response.status_code == 200

def test_fetcher_no_auth(client):
    url = '/api/gettimeseries'
    json_from_trainer['auth_json'] = {}
    no_auth_json = json_from_trainer
    no_auth_str = json.dumps(no_auth_json)

    response = client.get(url, query_string={'query':no_auth_str})
    assert b'Bad Request' in response.get_data()
    assert response.status_code == 400

def test_fetcher_no_query(client):
    url = '/api/gettimeseries'
    json_from_trainer['query_json'] = {}
    no_query_json = json_from_trainer
    no_query_str = json.dumps(no_query_json)

    response = client.get(url, query_string={'query':no_query_str})
    assert b'Bad Request' in response.get_data()
    assert response.status_code == 400