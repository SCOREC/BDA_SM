from flask import request, abort, Response
from trainer.src.exceptions import MKOTypeException
from sampler import app
from uuid import uuid4
from trainer.src.MKO import MKO
import json
import traceback

def get_input(field, args, return_none=False):
    if field not in args:
        if not return_none:
            abort(Response("'{}' not in args".format(field), 400))
        else:
            return None

    return args[field]

cache = {}

@app.route("/upload_mko", methods=["POST"])
def upload_mko():
    model_mko = get_input("model_mko", request.args)
    mko_id = str(uuid4())

    try:
        cache[mko_id] = MKO.from_b64str(model_mko)
    except Exception as e:
        return Response(str(e), 500)

    response_text = {
        "mko_id": mko_id
    }

    return Response(json.dumps(response_text), 200)

@app.route("/sample", methods=["POST"])
def sample():
    mko_id = get_input("mko_id", request.args)
    xs = get_input("x", request.args)
    samples = get_input("samples", request.args)

    if mko_id not in cache:
        return Response("id '{}' not uploaded".format(mko_id), 400)

    try:
        xs = list(json.loads(xs))
    except Exception as e:
        return Response("Format 'x' as array of floats")

    try:
        ys = cache[mko_id].make_inference(xs, samples).tolist()
    except MKOTypeException as e:
        return Response(str(e), 400)
    except Exception as e:
        return Response(traceback.format_exc(), 500)

    response_text = {
        "y": ys
    }
    return Response(json.dumps(response_text), 200)



@app.route("/remove_mko", methods=["POST"])
def remove_mko():
    mko_id = get_input("mko_id", request.args)

    if mko_id not in cache:
        return Response("id '{}' not uploaded".format(mko_id), 400)

    del cache[mko_id]

    return Response("success", 200)