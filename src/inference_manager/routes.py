from flask import request, abort, Response
from sampler import app
from subprocess import Popen, PIPE, STDOUT
import json

executable_path = "python -m analyzers.src.analyzers".split(" ")

def get_input(field, args, return_none=False):
    if field not in args:
        if not return_none:
            abort(Response("'{}' not in args".format(field), 400))
        else:
            return None

    return args[field]

def start_process(*args):
    return Popen([*executable_path, *args], stdin=PIPE, stdout=PIPE, stderr=STDOUT)

def start_and_send(data, *args):
    p = start_process(args)
    p.communicate(input=data.encode())

@app.route("/Infer/sample", methods=["POST"])
def sample():
    model_mko = get_input("model_mko", request.args)
    samples = get_input("sample_num", request.args)
    data_arr = get_input("data_array", request.args)
    sampler_uri = get_input("sampler_uri")

    data_to_send = {
        "model_mko": model_mko,
        "sample_num": samples,
        "data_arrray": data_arr,
        "sampler_uri": sampler_uri
    }

    start_and_send(json.dumps(data_to_send), "sample")
    return Response("success", 200)

    

@app.route("/Analyze/stat", methods=["POST"])
def stat():
    model_mko = get_input("model_mko", request.args)
    data_arr = get_input("data_array", request.args)
    sampler_uri = get_input("sampler_uri")

    data_to_send = {
        "model_mko": model_mko,
        "data_array": data_arr,
        "sampler_uri": sampler_uri
    }

    start_and_send(json.dumps(data_to_send), "stat")
    return Response("success", 200)

@app.route("/Analyze/Integrator", methods=["POST"])
def integrate():
    model_mko = get_input("model_mko", request.args)
    data_arr = get_input("data_array", request.args)
    funct_table = get_input("function_table", request.args)
    sampler_uri = get_input("sampler_uri")

    data_to_send = {
        "model_mko": model_mko,
        "data_array": data_arr,
        "function_table": funct_table,
        "sampler_uri": sampler_uri
    }

    start_and_send(json.dumps(data_to_send), "integrate")
    return Response("success", 200)


# to work on and decide some endpoints
# @app.route("/Analyze/*")
# def matplotlib_*():
#     pass