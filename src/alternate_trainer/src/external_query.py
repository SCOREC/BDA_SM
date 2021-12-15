import requests
from src.exceptions import ConnectionException, InputException
import json

# valid input json to the fetcher should contain these fields
# json_from_trainer = {
#     "auth_json" : {"authenticator": "abolajiDemo",
#                 "password": "memphis",
#                 "name": "Dami06",
#                 "role": "rpi_graphql",
#                 "url": "https://rpi.cesmii.net/graphql"
#                 },
#    "query_json" : {"tag_ids": ["917","907","909"],
#                 "start_time": "2021-00-23T20:51:40.071032+00:00",
#                 "end_time": "now",
#                 "GMT_prefix_sign":"plus",
#                 "max_samples": 0
#     }
# }

def check_connection(resp: requests.Response, URI: str):
    if resp.status_code != 200:
        raise ConnectionException(URI, resp.text)

def query_fetcher(URI: str, args: str) -> str:
    params = {
        "query": args
    }

    resp = requests.get("{}/api/gettimeseries".format(URI), params=params)
    check_connection(resp, URI)
    return resp.text

def get_http(URI: str) -> str:
    resp = requests.get(URI)
    check_connection(resp, URI)
    return resp.text

def post_result_cache(URI: str, username: str, claim_check: str, generation_time: float, mko_json: str):
    params = {
        "claim_check": claim_check,
        "generation_time": int(generation_time),
        "username": username
    }

    resp = requests.post(URI, params=params, data=mko_json)
    check_connection(resp, URI)