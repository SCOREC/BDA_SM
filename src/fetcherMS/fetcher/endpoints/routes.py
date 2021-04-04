from fetcher.endpoints import api
from flask import request
from .get_time_series import perform_get_time_series
import json
import numpy as np
from werkzeug.exceptions import BadRequest

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
            raise BadRequest('auth_json object or query_json not found in trainer JSON')
    else:
        raise BadRequest('Invalid Trainer JSON')
    matched_data = get_matching_dates(returned_json, query_json)
    return matched_data


def get_matching_dates(nums_json, query_json, debug=False, opt = 0):
    '''
    This routine takes a json object returned from the SM platform,
    1) It parses from starting date incrementally for each entry and confirms that the delta are the same
    2) It drops each row that doesnt have complete entries of matchind dates
    3) It returns the filtered object with completely matching rows and columns
    '''
    debug = True    #ABJ
    nums = json.dumps(nums_json)
    item_dict = json.loads(nums)
    dict_len = len(item_dict['data']['getRawHistoryDataWithSampling'])
    inner_dict = item_dict['data']['getRawHistoryDataWithSampling']

    # ABJ: approach 1: 2D array with matching ts (y) vs ids (x)
    time_set = set()
    ts_map = {}
    for i in range(dict_len):
        # get the content
        id = inner_dict[i]['id']
        dt = inner_dict[i]['dataType']
        if dt == "FLOAT":
            data_type = "floatvalue"
        elif dt == "INT":
            data_type = "intvalue"
        value = inner_dict[i][data_type]
        ts = inner_dict[i]["ts"]

        # hack to get a unique key for each entry in my json
        ts_map[ts+id] = value

        # create the time set to serve as my y_label
        if ts not in time_set:
            time_set.add(ts)

    if debug: print(ts_map.values())

    # get the ids (x label) and time (y labels)
    ids = query_json['tag_ids']
    sorted_ts = sorted(time_set)
    if debug: print("ids: ",ids, "\n ts: ", sorted_ts)

    # create a 2D array
    ts_data = [[None] * len(ids) for i in range(len(sorted_ts))]
    rows_to_drop = []

    for y, ts in enumerate(sorted_ts):
        for x, id in enumerate(ids):
            value = ts_map[ts+id]
            if value:
                ts_data[y][x] = value
            else:
                # get the rows to be dropped
                rows_to_drop.append(y)
                break

    # remove all rows that have an invalid entry
    ts_data = [row for i, row in enumerate(ts_data) if i not in rows_to_drop]
    if debug: print("ts_data: ", ts_data)

    # drop corresponding time labels
    sorted_ts = [elem for i, elem in enumerate(sorted_ts) if i not in rows_to_drop]
    if debug: print("sorted_ts: ", sorted_ts)

    # create the json object to be returned to the trainer
    sorted_js = {
        "y_labels": sorted_ts, 
        "x_labels" : ids,
        "data" : ts_data
    }
    
    if opt:
        print(" write the code for this option and probably compare timing")
    # approach 2: using numpy ???
    # np_2d_arr = [np.array(e) for e in inner_dict]
    # print("np shape is: ", np_2d_arr)

    # all time match outputs are sorted to avoid errors
    return sorted_js