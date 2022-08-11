from server.endpoints import api
from flask import request
from .get_time_series import perform_get_time_series
from .get_data import get_data
from .get_equipment_types import Perform_getEquipmentTypes
from .get_equipments import Perform_getEquipments
import json
from werkzeug.exceptions import BadRequest

@api.route('/echo', methods = ['GET'])
def echo():
    request_data = request.args.get('query')  # type: ignore
    return request_data

@api.route('/getdata', methods = ['GET'])
def getdata():
    request_data = json.loads(request.args.get('query'))  # type: ignore
    print(request_data)
    auth_json = None
    query_json = None
    if request_data:
        if 'auth_json' in request_data and 'get_data' in request_data:
            auth_json = request_data['auth_json']
            query_json = request_data['get_data']

            if not query_json:
                raise BadRequest('No input in the query')
            elif not 'Equipment' in query_json:
                raise BadRequest('No Equipment name found in the query')
            elif not 'Attribute' in query_json:
                raise BadRequest('No Attribute found in the query')

            return_json = get_data(auth_json, query_json)

        else:
            raise BadRequest("no auth and query data in request")

    else:
        raise BadRequest("Invalid Trainer Json")

    if not return_json:
        raise ValueError(' No JSON returned from CESMII')
    return return_json

@api.route('/getEquipment', methods = ['GET'])
def getEquipment():
    request_data = json.loads(request.args.get('query'))  # type: ignore
    auth_json = None
    if request_data:
        if 'auth_json' not in request_data: raise BadRequest("no auth and query data in request")
        auth_json = request_data['auth_json']
        return_json = Perform_getEquipmentTypes(auth_json)
    else:
        raise BadRequest("Invalid Trainer Json")
    if not return_json:
        raise ValueError(' No JSON returned from CESMII')
    return return_json

@api.route('/getEquipmentTypes', methods = ['GET'])
def getEquipmentTypes():
    request_data = json.loads(request.args.get('query'))  # type: ignore
    auth_json = None
    if request_data:
        if 'auth_json' not in request_data:
            raise BadRequest("no auth and query data in request")
        auth_json = request_data['auth_json']
        return_json = Perform_getEquipmentTypes(auth_json)
    else:
        raise BadRequest("Invalid Trainer Json")
    if not return_json:
        raise ValueError(' No JSON returned from CESMII')
    return return_json

@api.route('/gettimeseries', methods=['GET'])
def gettimeseries():
    
    request_data = json.loads(request.args.get('query'))  # type: ignore
    auth_json = None
    query_json = None
    # return request_data 
    if request_data:
        if 'auth_json' in request_data and 'query_json' in request_data:
            auth_json = request_data['auth_json']
            query_json = request_data['query_json']

            # set the GMT time_zone prefix sign
            if query_json and 'GMT_prefix_sign' in query_json:
                if query_json['GMT_prefix_sign'] == 'plus':
                    GMT_prefix = '+'
                else:
                    GMT_prefix = '-'
            else:
                raise BadRequest('GMT_prefix_sign not found')

            if 'start_time' and 'end_time' in query_json:
                query_json['start_time'] = query_json['start_time'].replace(" ",GMT_prefix)
                query_json['end_time'] = query_json['end_time'].replace(" ",GMT_prefix)
            else:
                raise BadRequest('start_time and/ or end_time not found')

            print(request_data['query_json']['start_time'])
            returned_json = perform_get_time_series(auth_json, query_json)
        else:
            raise BadRequest('auth_json object or query_json not found in trainer JSON')
    else:
        raise BadRequest('Invalid Trainer JSON')
    matched_data = get_matching_dates(returned_json, query_json)
    return matched_data
    return returned_json

def get_matching_dates(item_dict, query_json, debug=False, opt=0):
    '''
    This routine takes a json object returned from the SM platform,
    1) It parses from starting date incrementally for each entry and confirms that the delta are the same
    2) It drops each row that doesnt have complete entries of matching dates
    3) It returns the filtered object with completely matching rows and columns
    '''
    dict_len = len(item_dict['data']['getRawHistoryDataWithSampling'])
    inner_dict = item_dict['data']['getRawHistoryDataWithSampling']

    # ABJ: approach 1: 2D array with matching ts (y) vs ids (x)
    time_set = set()
    ts_map = {}
    for i in range(dict_len):
        # get the content
        id = inner_dict[i]['id']
        content_type = inner_dict[i]['dataType']
        if content_type == "FLOAT":
            data_type = "floatvalue"
        elif content_type == "INT":
            data_type = "intvalue"
        else:
            raise ValueError('content_type "{}" unsupported'.format(content_type))
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
    
    # TODO: complete  the numpy approach
    if opt:
        print(" write the code for this option and probably compare timing")
    # approach 2: using numpy ???
    # np_2d_arr = [np.array(e) for e in inner_dict]
    # print("np shape is: ", np_2d_arr)

    # all time match outputs are sorted to avoid errors

    # TODO: confirm a consistent delta_t across the entire data set and/or only use the handed delta_t
    return sorted_js