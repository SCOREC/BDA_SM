import pytest
import responses
import requests
import json
from tests.conftest import *

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

@responses.activate
def test_home(client):
    result = client.get('/fetcher_home')
    assert result.status_code == 200

@responses.activate
def test_get_ts(mock_fetcher_param, mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_fetcher_param["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        json=mock_resp_data,
        status=200,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_fetcher_param["query"]})
    assert 'data' in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

@responses.activate
def test_get_ts_invalid_auth(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_auth["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid auth_json",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_auth["query"]})
    resp = requests.get(url)
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

@responses.activate
def test_get_ts_invalid_query(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_query["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid query_json",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_query["query"]})
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

@responses.activate
def test_get_ts_invalid_user(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_user["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid user",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_user["query"]})
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

@responses.activate
def test_get_ts_invalid_pwd(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_pwd["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid password",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_pwd["query"]})
    resp = requests.get(url)
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

@responses.activate
def test_get_ts_invalid_name(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_name["query"])
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid name",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_name["query"]})
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url
    assert 'query' in responses.calls[0].request.params

@responses.activate
def test_get_ts_invalid_role(mock_resp_data):
    uri = "http://localhost:8080/api/gettimeseries"
    query_str = json.dumps(mock_invalid_role["query"])
    # print(query_str)
    url = uri + f'?query={query_str}'

    responses.add(
        method=responses.GET,
        url=url,
        body="Invalid role",
        status=404,
        match_querystring=False,
    )
    resp = requests.get(uri, params={"query": mock_invalid_role["query"]})
    assert 'data' not in responses.calls[0].response.text
    assert 'gettimeseries' in responses.calls[0].request.url

# https://github.com/getsentry/responses
# https://medium.com/@vladbezden/how-to-mock-flask-request-object-in-python-fdbc249de504
# https://medium.com/analytics-vidhya/pytest-mocking-cheatsheet-dcebd84876e3