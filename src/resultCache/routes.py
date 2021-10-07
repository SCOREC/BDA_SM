from flask import request, abort, Response
from resultCache import app
from resultCache.file_daemon import FileHandler
from resultCache.config import config

file_handler: FileHandler = None

@app.before_first_request
def on_start():
    global file_handler
    file_handler = FileHandler(config.min_expiry_time, config.max_expiry_time, config.directory)


@app.route('/store_result', methods=['POST'])
def store():
    username = request.args['username']
    claim_check = request.args["claim_check"]
    try:
        generation_time = int(request.args["generation_time"])
    except ValueError:
        abort(Response("'{}' not of type 'int'".format(request.args["generation_time"]), 400))
    data = request.data

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    file_handler.put(username, claim_check, generation_time, data)    
    return Response("success", 200)


@app.route("/get_result", methods=["GET"])
def get():
    username = request.args['username']
    claim_check = request.args["claim_check"]

    if file_handler == None:
        abort(Response("file handler not initialized", 500))

    try: 
        data = file_handler.get(username, claim_check, str)
    except Exception as e:
        abort(Response(e.with_traceback, 500))
    
    if data == None:
        return Response("'/{}/{}' not found".format(username, claim_check), 404)

    return Response(data, 200)

@app.route("/close", methods=["POST"])
def close():
    file_handler.end()


    



    
