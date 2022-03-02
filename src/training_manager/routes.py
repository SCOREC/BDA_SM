from tempfile import NamedTemporaryFile
from flask import request, abort, Response
from training_manager import app
from subprocess import Popen

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

# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# model_name: name of the model to be created
# creates mko and posts to resultChache
@app.route('/create_MKO', methods=['POST'])
def create_MKO():
    model_name = get_input("model_name", request.args)
    URI, username, claim_check = get_post_args(request.args)
    Popen([*executable_path, username, claim_check, URI, "--create", "--name", "--delete", model_name])
    return Response("success", 200)

# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# type: type of portion to add (eg. data, hyperparmams, etc.)
# to_add: json string of portion to add
# model_MKO: json string of mko 
# merges the to_add json with the model_MKO under the type field
@app.route('/add_component', methods=['POST'])
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
@app.route('/train', methods=['POST'])
def train():
    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--delete", "--train"])
    return Response("success", 200)