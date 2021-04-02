from fetcher.endpoints import api
from flask import request
from .get_time_series import perform_get_time_series
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
            # return returned_json
        else:
            raise ValidationError('auth_json object or query_json not found in trainer JSON')
    else:
        raise ValidationError('Invalid Trainer JSON')
    matched_data = get_matching_dates(returned_json, query_json)
    return matched_data


def get_matching_dates(nums_json, query_json, debug=False):
    '''
    This routine takes a json object returned from the SM platform,
    1) It parses from starting date incrementally for each entry and confirms that the delta are the same
    2) It drops each row that doesnt have complete entries of matchind dates
    3) It returns the filtered object with completely matching rows and columns
    '''
    # debug = True    #ABJ
    nums = json.dumps(nums_json)
    item_dict = json.loads(nums)
    dict_len = len(item_dict['data']['getRawHistoryDataWithSampling'])
    inner_dict = item_dict['data']['getRawHistoryDataWithSampling']

    # create a sorted time list
    time_set = set()
    ts_map = {}
    for i in range(dict_len):
        if debug: print(inner_dict[i])

        # get the content
        id = inner_dict[i]['id']
        dt = inner_dict[i]['dataType']
        if dt == "FLOAT":
            data_type = "floatvalue"
        elif dt == "INT":
            data_type = "intvalue"
        value = inner_dict[i][data_type]
        ts = inner_dict[i]["ts"]

        # hack to get a unique entry for each entry in my json
        ts_map[ts+id] = value

        # create the time set to serve as my y_label
        if ts not in time_set:
            time_set.add(ts)

    # get the ids label (x)
    ids = query_json['tag_ids']
    if debug:
        for id in ids:
            print(id)
    
    # get the time labels (y)
    sorted_time = sorted(time_set)

    # define the 2D DS to house the objects
    ts_data = [[None] * len(ids) for i in range(len(sorted_time))]    # 2D array to hold data

    # populate the 2D DS - loop through all available time
    for y, ts in enumerate(sorted_time):
        for x, id in enumerate(ids):
            print(ts_map[ts+id])
            value = ts_map[ts+id]
            # if this is a valid entry, insert it at the correct location in the index
            if value:
                ts_data[y][x] = value
            # numpy ???

    return nums