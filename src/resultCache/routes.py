from flask import request, abort, Response
from resultCache import app
from resultCache.file_daemon import FileHandler
from resultCache.config import config

file_handler: FileHandler = None

def set_config(new_config):
    global config
    config = new_config

@app.before_first_request
def on_start():
    global file_handler
    file_handler = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)


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
def store():
    check_input('username', request.args)
    check_input('claim_check', request.args)
    check_input('generation_time', request.args)


    username = request.args['username']
    claim_check = request.args["claim_check"]
    try:
        generation_time = int(request.args["generation_time"])
    except ValueError:
        abort(Response("'{}' not of type 'int'".format(request.args["generation_time"]), 400))

    data = request.data

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try:
        file_handler.put(username, claim_check, generation_time, data)    
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
def get():
    check_input('username', request.args)
    check_input('claim_check', request.args)

    username = request.args['username']
    claim_check = request.args["claim_check"]

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = file_handler.get(username, claim_check, str)
    except Exception as e:
        app.log_exception(e)
        abort(Response(e.with_traceback, 500))
    
    if data == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    return Response(data, 200)
    