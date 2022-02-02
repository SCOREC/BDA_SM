from flask import request, abort, Response
from training_manager import app
import os

def get_input(field, args):
    if field not in args:
        abort(Response("'{}' not in args".format(field), 400))

    return args[field]

def get_post_args(args):
    URI = get_input("result_cache_URI", args)
    username = get_input("username", args)
    claim_check = get_input("claim_check", args)
    return (URI, username, claim_check)

@app.route('/create_MKO', methods=['POST'])
def create_MKO():
    model_name = get_input("model_name", request.args)
    post_args = get_post_args(request.args)
    os.system("python -m ")
    # try:
    #     trainer.create_mko(model_name, post_args)
    # except UserError as e:
    #     abort(Response("USER ERROR: {}".format(e), 400))
    # except Exception as e:
    #     abort(Response("ERROR: {}".format(e), 500))


@app.route('/add_component', methods=['POST'])
def add_data():
    add_type = get_input("type", request.args)
    json_to_add = get_input("to_add", request.args)
    mko = get_input("model_MKO", request.args)
    # post_args = get_post_args(request.args)
    # try:
    #     trainer.add_mko_create_file(mko, add_type, json_to_add, post_args)
    # except UserError as e:
    #     abort(Response("USER ERROR: {}".format(e), 400))
    # except Exception as e:
    #     abort(Response("ERROR: {}".format(e), 500))

@app.route('/delete_param', methods=['POST'])
def delete_param():
    pass

@app.route('/train', methods=['POST'])
def delete_param():
    mko = get_input("model_MKO", request.args)
    post_args = get_post_args(request.args)
    # try:
    #     trainer.train_mko(mko, post_args)
    # except UserError as e:
    #     abort(Response("USER ERROR: {}".format(e), 400))
    # except Exception as e:
    #     abort(Response("ERROR: {}".format(e), 500))