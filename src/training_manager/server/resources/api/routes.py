from flask import request
from flask.wrappers import Response
from tempfile import NamedTemporaryFile
from subprocess import Popen
import server.trainer

from server.resources.api import bp

@bp.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "Hello World!"



executable_path = "python -m trainer.src.trainer".split(" ")

def get_input(field, args):
    if field not in args:
        abort(Response("'{}' not in args".format(field), 400))

    return args[field]

def get_post_args(args):
    URI = get_input("result_cache_URI", args)
    username = get_input("username", args)
    claim_check = get_input("claim_check", args)
    return (URI, username, claim_check)

def save_file(data):
    f = NamedTemporaryFile("w", delete=False)
    f.write(data)
    f.close()
    return f.name

# username: username of user
# model_name: name of the model to be created
@bp.route('/create_MKO', methods=['POST'])
def create_MKO():
    model_name = request.values.get("model_name")
    username = request.values.get("username")
    claim_check = server.trainer.create_mko(model_name, username)
    return ({'claim_check': claim_check}, 200)

# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# type: type of portion to add (eg. data, hyperparmams, etc.)
# to_add: json string of portion to add
# model_MKO: json string of mko 
# merges the to_add json with the model_MKO under the type field
@bp.route('/add_component', methods=['POST'])
def add_data():
    add_type = get_input("type", request.args)
    json_to_add = get_input("to_add", request.args)
    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    # save mko to temp file get abs location and pass to popen
    # potential problem that temp get filled up but never deleted - should i wait for completion in this case?
    add_loc = save_file(json_to_add)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--add", "--delete", add_type, add_loc])
    return Response("success", 200)
    
# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# model_MKO: json string of mko 
# trains the model specified by the parameters
@bp.route('/train', methods=['POST'])
def train():
    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--delete", "--train"])
    return Response("success", 200)