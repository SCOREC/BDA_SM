import imp
from multiprocessing import AuthenticationError
from flask import request, abort, jsonify
from flask.wrappers import Response
from server.file_daemon import FileHandler
from datetime import datetime, timedelta
from server.claim_check import ClaimCheck

from server.resources.api import bp
from server import app
import server.file_daemon

def check_input(field, args):
    if field not in args:
        abort(Response("'{}' not in args".format(field), 400))

@bp.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "API: Hello World!"

@bp.route ('/new_claim_check', methods =['GET'])
def new_claim_check():
  try:
    username = request.values['username']
    offset = int(request.values.get('offset', 0))
    claim_check = ClaimCheck(username, offset)
    return jsonify({"claim_check": claim_check.token})
  except Exception as err:
    return Response("Bad request", 400)

"""
Descrption: Stores input data for later use
Arguments:
    username: str
    claim_check: str
    generation_time: int - time it took to generate data
"""
@bp.route('/store_result', methods=['POST'])
def store_result():
    check_input('username', request.args)
    check_input('claim_check', request.args)
    check_input('generation_time', request.args)

    username = request.args['username']
    token = request.args["claim_check"]

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    try:
        generation_time = int(request.args["generation_time"])
    except ValueError:
        abort(Response("'{}' not of type 'int'".format(request.args["generation_time"]), 400))

    data = request.data.decode("utf-8")

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        server.file_daemon.file_handler.put(username, claim_check.shortname, generation_time, data)    
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))

    return Response("success", 200)


"""
Description: Retrieves data previously stored, deletes data upon retrieval
Arguments:
    username: str   
    claim_check: str
"""
@bp.route("/get_result", methods=["GET"])
def get_result(): # handle the case of get result being called before get status

    try:
      username = request.args['username']
      token = request.args["claim_check"]
      remove = request.values.get("please_retain", "False") != "True"
    except ValueError as err:
      abort(Response("Badly formed request: {}".format(err), 400))

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = server.file_daemon.file_handler.get(username, claim_check.shortname, remove)
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))
    
    if len(data) == 0:
        return Response("'/{}/{}' not found".format(username, claim_check), 204)

    return Response(data, 200)
    

"""
Descrption: Updates entry with status, creates entry if it doesn't exist
Arguments:
    username: str
    claim_check: str
"""
@bp.route('/update_status', methods=['POST'])
def store_status(): #should set generation time to max

    try:
      username = request.args['username']
      token = request.args["claim_check"]
    except ValueError as err:
      abort(Response("Badly formed request: {}".format(err), 400))

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    generation_time = app.config['MAX_EXPIRY_TIME']
    status = request.data.decode("utf-8")

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        status = float(status)
    except ValueError:
        abort(Response("'{}' not of type 'float'".format(status), 400))

    if status < 0 or status >= 1:
        abort(Response("0 <= status < 1; status was '{}'".format(status), 400))

    try:
        server.file_daemon.file_handler.update_status(username, claim_check.shortname, generation_time, status)    
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))

    return Response("success", 200)


"""
Description: Gets the current status of result as percentage
Arguments:
    username: str   
    claim_check: str
"""
@bp.route("/get_status", methods=["GET"])
def get_status():
    try:
      username = request.args['username']
      token = request.args["claim_check"]
    except ValueError as err:
      abort(Response("Badly formed request: {}".format(err), 400))

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = server.file_daemon.file_handler.get_most_recent_status(username, claim_check.shortname)
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))
    
    if data == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    return Response(str(data), 200)


"""
Descrption: Stores any errors associated with 
Arguments:
    username: str
    claim_check: str
"""
@bp.route('/put_error', methods=['POST'])
def store_error():

    try:
      username = request.args['username']
      token = request.args["claim_check"]
    except ValueError as err:
      abort(Response("Badly formed request: {}".format(err), 400))

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    generation_time = app.config['MAX_EXPIRY_TIME']
    errors = request.data.decode("utf-8")

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        server.file_daemon.file_handler.update_error(username, claim_check.shortname, generation_time, errors)    
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))

    return Response("success", 200)


"""
Description: Gets the current time estimate of request completion
Arguments:
    username: str   
    claim_check: str
"""
@bp.route("/get_eta", methods=["GET"])
def get_eta():
    try:
      username = request.args['username']
      token = request.args["claim_check"]
    except ValueError as err:
      abort(Response("Badly formed request: {}".format(err), 400))

    try:
      claim_check = ClaimCheck.from_jwt(token)
      claim_check.validate_or_throw(username, AuthenticationError)
    except Exception as err:
      abort(Response("Not valid claim check for user {}".format(username), 401))

    if server.file_daemon.file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        time = server.file_daemon.file_handler.get_status(username, claim_check.shortname)
        rate = server.file_daemon.file_handler.get_rate(username, claim_check.shortname)
    except Exception as err:
        abort(Response("File handler error: {}".format(err), 500))
    
    if time == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    if rate == None:
        return Response("updates < 2", 500)

    time = time[-1][1]

    return Response(str(rate * time), 200)
