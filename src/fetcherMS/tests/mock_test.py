try:
    import pytest
    import fetcher
    # import requests
    # import response
    # import requests_mock
    import unittest
    from unittest.mock import patch
    from fetcher import app, fetcher_home
    import flask
except Exception as e:
    print("Some modules are missing {}".format(e))

try:
    from unittest import mock
except ImportError:
    import mock


# @pytest.fixture
# def app(mocker):
#     mocker.patch("fetcher.fetcher_home", return_value={})
#     return fetcher.app


class BasicTests(unittest.TestCase):
    # @mock.patch(app.requests.get)
    def test_request_with_decorator(self, mock_get):
        "Mocking with the decorator"
        fake_str = 'This is fetcher home!'
        with patch('')
        mock_get.return_value.status_code = 200
        response = app()

        self.assertEqual(response.status_code, 200)

'''
# This should be a replacement to request.get
def mocked_request_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://127.0.0.1:8080/fetcher_home':
        return MockResponse("fetcher_home", 200)
    
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

# # Flask attempt
# def test_fetcher(client):
#     res = client.get("/")
#     assert res.status_code == 200

