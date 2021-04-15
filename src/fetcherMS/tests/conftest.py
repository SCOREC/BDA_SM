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

# https://stackoverflow.com/questions/54050502/use-mock-server-in-testing-flask-app-using-pytest

auth_js = {"authenticator": "abolajiDemo",
                "password": "memphis",
                "name": "Dami06",
                "role": "rpi_graphql",
                "url": "https://rpi.cesmii.net/graphql" }

query_js = {"tag_ids": [ "984","997", "996"],
                "start_time": "2020-01-23T20:51:40.071032+00:00", "GMT_prefix_sign":"plus",
                "end_time": "now",
                "max_samples": 0  }

@pytest.fixture(autouse=True)
def client():
    client = app.test_client()
    yield client

@pytest.fixture
def flask_app_mock():
    """Flask application set up."""
    app_mock = Flask(__name__)
    return app_mock

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
    ]}
    yield res_json

@pytest.fixture
def mock_fetcher_param():
    param = {"query": {
    "auth_json" : auth_js,
   "query_json" : query_js}}
    yield param

# The following variables are non-mocked as they are only used once for each of the testcases

mock_invalid_auth = {"query": {
    "auth_json" : {},
    "query_json" : query_js}}

mock_invalid_query = {"query": {
    "auth_json" : auth_js,
    "query_json" : {} }}

auth_holder = auth_js.copy()
auth_holder["authenticator"] = ""
mock_invalid_user = {"query": {
    "auth_json" : auth_holder,
    "query_json" : query_js}}

auth_holder = auth_js.copy()
auth_holder["password"] = ""
mock_invalid_pwd = {"query": {
    "auth_json" : auth_holder,
    "query_json" : query_js}}

auth_holder = auth_js.copy()
auth_holder["name"] = ""
mock_invalid_name = {"query": {
    "auth_json" : auth_holder,
    "query_json" : query_js}}

auth_holder = auth_js.copy()
auth_holder["role"] = ""
mock_invalid_role = {"query": {
    "auth_json" : auth_holder,
    "query_json" : query_js}}