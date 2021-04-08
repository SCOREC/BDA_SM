try:
    import pytest
    import fetcher
    # import requests
    # import response
    # import requests_mock
    import unittest
    from unittest.mock import patch
    from fetcher import create_app, configure_app
except Exception as e:
    print("\nSome modules are missing {}".format(e))

try:
    from unittest import mock
except ImportError:
    import mock


@pytest.fixture
def app(mocker):
    mocker.patch("fetcher.configure_app.fetcher_home", return_value='This is fetcher home!')
    app = create_app()
    return app

# def client(app):
#     return app.test_client()

# def test_home_funky(client):
#     assert True
    # res = client.get("/fetcherhome")
    # assert res.json == {'res': 'This'}

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

