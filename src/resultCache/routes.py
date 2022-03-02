from os import getenv
from flask import request, abort, Response
from resultCache import app
from resultCache.file_daemon import FileHandler
from resultCache.config import config
from uuid import uuid4

file_handler: FileHandler = None

def set_config(new_config):
    global config
    config = new_config

@app.before_first_request
def on_start():
    global file_handler

    min_expiry_time = getenv("RC_MIN_EXP_TIME") if getenv("RC_MIN_EXP_TIME") else config.min_expiry_time
    max_expiry_time = getenv("RC_MAX_EXP_TIME") if getenv("RC_MAX_EXP_TIME") else config.max_expiry_time

    file_handler = FileHandler(min_expiry_time, max_expiry_time, config.rate_average_window, config.directory)


def check_input(field, args):
    if field not in args:
        abort(Response("'{}' not in args".format(field), 400))


"""
Descrption: Stores input data for later use
Arguments:
    username: str
    claim_check: str
    generation_time: int - time it took to generate data
"""
@app.route('/store_result', methods=['POST'])
def store_result():
    check_input('username', request.args)
    check_input('claim_check', request.args)
    check_input('generation_time', request.args)


    username = request.args['username']
    claim_check = request.args["claim_check"]
    try:
        generation_time = int(request.args["generation_time"])
    except ValueError:
        abort(Response("'{}' not of type 'int'".format(request.args["generation_time"]), 400))

    data = request.data.decode("utf-8")

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        file_handler.put(username, claim_check, generation_time, data)    
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))

    return Response("success", 200)


"""
Descrption: Updates entry with status, creates entry if it doesn't exist
Arguments:
    username: str
    claim_check: str
"""
@app.route('/update_status', methods=['POST'])
def store_status(): #should set generation time to max
    check_input('username', request.args)
    check_input('claim_check', request.args)

    username = request.args['username']
    claim_check = request.args["claim_check"]
    generation_time = config.max_expiry_time

    status = request.data.decode("utf-8")

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        status = float(status)
    except ValueError:
        abort(Response("'{}' not of type 'float'".format(status), 400))

    if status < 0 or status >= 1:
        abort(Response("0 <= status < 1; status was '{}'".format(status), 400))

    try:
        file_handler.update_status(username, claim_check, generation_time, status)    
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))

    return Response("success", 200)


"""
Descrption: Stores any errors associated with 
Arguments:
    username: str
    claim_check: str
"""
@app.route('/put_error', methods=['POST'])
def store_error():
    check_input('username', request.args)
    check_input('claim_check', request.args)


    username = request.args['username']
    claim_check = request.args["claim_check"]
    generation_time = config.max_expiry_time
    errors = request.data.decode("utf-8")

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        file_handler.update_error(username, claim_check, generation_time, errors)    
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))

    return Response("success", 200)



"""
Description: Retrieves data previously stored, deletes data upon retrieval
Arguments:
    username: str   
    claim_check: str
"""
@app.route("/get_result", methods=["GET"])
def get_result(): # handle the case of get result being called before get status
    check_input('username', request.args)
    check_input('claim_check', request.args)

    username = request.args['username']
    claim_check = request.args["claim_check"]

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = file_handler.get(username, claim_check)
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))
    
    if data == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    return Response(data, 200)
    

"""
Description: Gets the current status of result as percentage
Arguments:
    username: str   
    claim_check: str
"""
@app.route("/get_status", methods=["GET"])
def get_status():
    check_input('username', request.args)
    check_input('claim_check', request.args)

    username = request.args['username']
    claim_check = request.args["claim_check"]

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = file_handler.get_status(username, claim_check)
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))
    
    if data == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    data = data[-1][1]

    return Response(data, 200)

"""
Description: Gets the current time estimate of request completion
Arguments:
    username: str   
    claim_check: str
"""
@app.route("/get_eta", methods=["GET"])
def get_status():
    check_input('username', request.args)
    check_input('claim_check', request.args)

    username = request.args['username']
    claim_check = request.args["claim_check"]

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        time = file_handler.get_status(username, claim_check)
        rate = file_handler.get_rate(username, claim_check)
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))
    
    if time == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    if rate == None:
        return Response("updates < 2", 500)

    time = time[-1][1]

    return Response(rate * time, 200)


"""
Description: Gets the current time estimate of request completion
"""
@app.route("/get_claim_check", methods=["GET"])
def get_status():
    data = str(uuid4())
    return Response(data, 200)
