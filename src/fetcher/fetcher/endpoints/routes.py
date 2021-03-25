from fetcher.endpoints import api
from flask import request
from .get_time_series import perform_get_time_series

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
#                 "max_samples": 0
#     }
# }

# <PORT>/api/gettimeseries
@api.route('/gettimeseries', methods=['GET'])
def gettimeseries():
    request_data = request.get_json()
    auth_json = None
    query_json = None
    
    if request_data:
        if 'auth_json' in request_data and 'query_json' in request_data:
            auth_json = request_data['auth_json']
            query_json = request_data['query_json']
            returned_json = perform_get_time_series(auth_json, query_json)
            return returned_json
        else:
            raise ValidationError('auth_json object or query_json not found in trainer JSON')
    else:
        raise ValidationError('Invalid Trainer JSON')