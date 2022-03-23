from tempfile import NamedTemporaryFile
from flask import request, abort, Response
from pandas import date_range
from training_manager import app
from subprocess import Popen
import json
from training_manager.defaults import Defaults

executable_path = "python -m trainer.src.trainer".split(" ")

def get_input(field, args, return_none=False):
    if field not in args:
        if not return_none:
            abort(Response("'{}' not in args".format(field), 400))
        else:
            return None

    return args[field]

def cast(var, type, name):
    if var != None:
        try:
            return type(var)
        except:
            abort(Response("'{}' not of type '{}'".format(name, type), 400))

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
    Popen([*executable_path, "--create", "--name", model_name, "--delete", username, claim_check, URI])
    return Response("success", 200)

# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# model_MKO: json string of mko 
# required fields:
#   - authenticator
#   - password
#   - name
#   - role
#   - graphql_url
#   - x_tags (must be a json list)
#   - y_tags (must be a json list)
#   - start_time
#   - end_time
#   - data_location
# adds data field to mko
@app.route('/add_data', methods=['POST'])
def add_data():
    # mandatory
    authenticator = get_input("authenticator", request.args)
    password = get_input("password", request.args)
    name = get_input("name", request.args)
    role = get_input("role", request.args)
    url = get_input("graphql_url", request.args)
    x_tags = get_input("x_tags", request.args)
    y_tags = get_input("y_tags", request.args)
    start_time = get_input("start_time", request.args)
    end_time = get_input("end_time", request.args)
    data_location = get_input("data_location", request.args)

    try:
        x_tags = json.loads(x_tags)
    except Exception:
        abort(Response("x_tags not JSON array", 400))
        
    try:
        y_tags = json.loads(y_tags)
    except Exception:
        abort(Response("y_tags not JSON array", 400))

    json_to_add = json.dumps(
        Defaults.get_fetcher_data_json(
            authenticator, 
            password, 
            name, 
            role, 
            url, 
            x_tags, 
            y_tags, 
            start_time, 
            end_time, 
            data_location
        )
    )

    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    add_loc = save_file(json_to_add)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--add", "data", add_loc, "--delete"])
    return Response("success", 200)


# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# model_MKO: json string of mko 
# required fields:
#   - data_shape
# optional fields:
#   - epochs
#   - batch_size
#   - optimizer
#   - learning_rate
#   - loss_function
#   - train_percent
# adds hyperparmeters field to mko
@app.route('/add_hparams', methods=['POST'])
def add_hparams():
    # mandatory
    data_shape = get_input("data_shape", request.args)
    
    # has defaults
    epochs = get_input("epochs", request.args, True)
    batch_size = get_input("batch_size", request.args, True)
    optimizer = get_input("optimizer", request.args, True)
    learning_rate = get_input("learning_rate", request.args, True)
    loss_function = get_input("loss_function", request.args, True)
    train_percent = get_input("train_percent", request.args, True)

    try:
        data_shape = json.loads(data_shape)
    except Exception:
        abort(Response("'data_shape' not of type list", 400))

    epochs = cast(epochs, int, "epochs")
    batch_size = cast(batch_size, int, "batch_size")
    learning_rate = cast(learning_rate, float, "learning_rate")
    train_percent = cast(train_percent, float, "train_percent")


    json_to_add = json.dumps(
        Defaults.get_hparams_json(
            loss_function,
            data_shape,
            epochs, 
            batch_size,
            optimizer,
            learning_rate,
            train_percent
        )
    )

    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    add_loc = save_file(json_to_add)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--add", "hparams", add_loc, "--delete"])
    return Response("success", 200)


# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# model_MKO: json string of mko 
# required fields:
#   - output_shape
# optional fields:
#   - final_activation_funct
#   - layers
#   - activation_funct
#   - units
#   - dropout_rate
# adds topology field to mko
@app.route('/add_topology', methods=['POST'])
def add_topology():
    # mandatory
    output_shape = get_input("output_shape", request.args)

    # has defaults
    final_activation_funct = get_input("final_activation_funct", request.args, True)
    layers = get_input("layers", request.args, True)
    activation_funct = get_input("activation_funct", request.args, True)
    units = get_input("units", request.args, True)
    dropout_rate = get_input("dropout_rate", request.args, True)

    output_shape = cast(output_shape, int, "output_shape")
    layers = cast(layers, int, "layers")
    units = cast(units, int, "units")
    dropout_rate = cast(dropout_rate, float, "dropout_rate")

    json_to_add = json.dumps(
        Defaults.get_topology_json(
            output_shape, 
            final_activation_funct, 
            layers, 
            activation_funct, 
            units, 
            dropout_rate
        )
    )

    mko = get_input("model_MKO", request.args)
    URI, username, claim_check = get_post_args(request.args)
    add_loc = save_file(json_to_add)
    mko_loc = save_file(mko)
    Popen([*executable_path, username, claim_check, URI, "-f", mko_loc, "--add", "topology", add_loc, "--delete"])
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
