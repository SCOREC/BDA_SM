try:
    import pytest
    import flask
    from flask import Flask
    import fetcher
    import responses
    import unittest
    from unittest.mock import patch
    from fetcher import create_app, configure_app, app
except Exception as e:
    print("\nSome modules are missing {}".format(e))

try:
    from unittest import mock
except ImportError:
    import mock



# @pytest.fixture
# def app(mocker):
#     mocker.patch("fetcher.configure_app.fetcher_home", return_value='This is fetcher home!')
#     app = create_app()
#     return app


# @pytest.fixture(scope="session", autouse=True)
# def clean_up():
#     yield
#     default_vals = {
#         "1": {"name": "ginger", "breed": "bengal", "price": 100},
#         "2": {"name": "sam", "breed": "husky", "price": 10},
#         "3": {"name": "guido", "breed": "python", "price": 518},
#     }

#     abs_file_path = os.path.abspath(os.path.dirname(__file__))
#     json_path = os.path.join(abs_file_path, "../", "test_api", "core", "vals.json")
#     with open(json_path, "w") as val_store:
#         json.dump(default_vals, val_store, indent=4)

# @pytest.fixture
# def client(mocker):
#     mocker.patch("fetcher.get_fetcher", return_value='bar')
#     app = create_app()
#     return app

# @fixture
# def client():
#     # add response
#     responses.add(responses.GET,
#         'http://localhost:8000',
#         json={'key': 'value'},
#         status=404
#     )
#     # do fixture stuff -> here it is yielding app test client
#     app = Flask(__name__)
#     app.config['TESTING'] = True
#     client = app.test_client() 

#     yield client
#     # https://stackoverflow.com/questions/54050502/use-mock-server-in-testing-flask-app-using-pytest


@pytest.fixture(autouse=True)
def client():
    # app.config['TESTING'] = True
    client = app.test_client()
    yield client

@pytest.fixture
def flask_app_mock():
    """Flask application set up."""
    app_mock = Flask(__name__)
    return app_mock

@pytest.fixture
def mock_fetcher_param():

    param = {"query": {
    "auth_json" : {"authenticator": "abolajiDemo",
                "password": "memphis",
                "name": "Dami06",
                "role": "rpi_graphql",
                "url": "https://rpi.cesmii.net/graphql"
                },
   "query_json" : {"tag_ids": [ "984","997", "996"],
                "start_time": "2020-01-23T20:51:40.071032+00:00", "GMT_prefix_sign":"plus",
                "end_time": "now",
                "max_samples": 0
    }
    }}
    yield param

@pytest.fixture
def mock_resp_data():
    res_json = {
    "data": [
        [
            215.94,
            907.3,
            1.2
        ],
        [
            225.94,
            910.3,
            6.2
        ],
        [
            229.94,
            911.3,
            10.2
        ],
        [
            232.94,
            919.3,
            15.2
        ],
        [
            236.94,
            924.3,
            16.2
        ],
        [
            215.94,
            907.3,
            1.2
        ],
        [
            225.94,
            910.3,
            6.2
        ],
        [
            229.94,
            911.3,
            10.2
        ],
        [
            232.94,
            919.3,
            15.2
        ],
        [
            236.94,
            924.3,
            16.2
        ]
    ],
    "x_labels": [
        "984",
        "997",
        "996"
    ],
    "y_labels": [
        "2021-01-01T22:14:42.049+00:00",
        "2021-01-02T23:14:42.049+00:00",
        "2021-01-03T00:14:42.049+00:00",
        "2021-01-03T01:14:42.049+00:00",
        "2021-01-03T02:14:42.049+00:00",
        "2021-04-01T22:14:42.049+00:00",
        "2021-04-02T23:14:42.049+00:00",
        "2021-04-03T00:14:42.049+00:00",
        "2021-04-03T01:14:42.049+00:00",
        "2021-04-03T02:14:42.049+00:00"
    ]}
    yield res_json