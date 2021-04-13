try:
    import pytest
    import flask
    from flask import Flask
    import fetcher
    import responses
    import requests
    import unittest
    from unittest.mock import patch
    import json
    from fetcher import create_app, configure_app, app
    from fetcher.endpoints.routes import gettimeseries
except Exception as e:
    print("\nSome modules are missing {}".format(e))

try:
    from unittest import mock
except ImportError:
    import mock

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

@responses.activate
def test_fetcher_home(client):
    result = client.get('/fetcher_home')
    assert result.status_code == 200

# https://github.com/getsentry/responses
@responses.activate
def test_get_ts(mock_fetcher_param, mock_resp_data):
    param = mock_fetcher_param
    res_json = mock_resp_data

    url = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(param["query"])
    url = url + f'?query={query_str}'

    responses.add(responses.GET, url, json=res_json, status=200)
    resp = requests.get(url)
    assert 'data' in responses.calls[0].response.text

# https://medium.com/@vladbezden/how-to-mock-flask-request-object-in-python-fdbc249de504
# def test_fetcher_home_2(mocker):
#     given_user = "samy"
#     req_mock = mocker.patch.object(flask, "request")
#     req_mock.headers.get.return_value = given_user
#     res = user_name()

# https://medium.com/analytics-vidhya/pytest-mocking-cheatsheet-dcebd84876e3
# def test_mock_home(flask_app_mock):
#     with flask_app_mock.app_context():
#         home = configure_app(flask_app_mock)
#         response = home()
#         assert response == "This is fetcher home!"


'''
@patch("fetcher.endpoints.routes.gettimeseries")
def test_get_time(mock_get_ts):
    # arrange data    
    ts_mock = mock.Mock(flask, "request")   # unsure of this
    mock_get_ts.return_value = '{"foo": "bar"}'

    # action
    # call the get time series - call the api route with the arguments
    with mock_get_ts.test_request_context('/gettimeseries', data={"query": {
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
    }}):
        actual_res = gettimeseries()

    # first_call = mock_get_ts.call_agrs_list[0]
    # assert_equals()

class BasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("setup class called")
    
    @classmethod
    def tearDownClass(cls):
        print("\n Tear down class called")

    def setUp(self):
        self.auth = 0 # create an initialized class variable
    
    def tearDown(self):
        print("function tear down called")

    # @mock.patch(fetcher.configure_app.fetcher_home.requests.get)
    # def test_request_with_decorator(self, mock_get):
    def test_home(self):
        "Mocking with the decorator"
        fake_str = 'This is fetcher home!'
        # with patch('fetcher.requests.get')
        # mock_get.return_value.status_code = 200
        # response = app()

        # self.assertEqual(response.status_code, 200)
    # def test_home_funky(self):
    #     assert True

# This should be a replacement to request.get
def mocked_request_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://127.0.0.1:8080/fetcher_home':
        return MockResponse("This is fetcher home!", 200)
    
    # add more conditions here
    return MockResponse(None, 400)

class FetcherTestCase(unittest.TestCase):

    @mock.patch('fetcher.request.get', side_effect=mocked_request_get)
    def test_fetcher(self, mock_get):
        json_data = fetcher_home('http://127.0.0.1:8080/fetcher_home')
        self.assertEqual(json_data, "fetcher_home")

if __name__ =="__main__":
    print(__name__)
    unittest.main()
    '''