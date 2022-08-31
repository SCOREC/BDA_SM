import requests
from externals.utilities import check_connection
from externals.exceptions import ConnectionException

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


def query_fetcher(URI: str, query: str, auth : str) -> str:
    params = {
        "as_csv" : "False",
        "as_json": "True",
        "query": query,
        "auth" : auth
    }
    full_url = "{}/api/timeseriesArrayById".format(URI.rstrip('/ '))
    resp = requests.get(full_url, params=params)
    check_connection(resp, full_url)
    return resp.text

def get_http(URI: str) -> str:
    resp = requests.get(URI)
    check_connection(resp, URI)
    return resp.text
