from flask import request, abort
from flask.wrappers import Response
from trainer.mko.exceptions import InputException, MKOTypeException
from sampler.server import app
from uuid import uuid4
from trainer.mko import MKO
import json
import traceback
import sys


def get_input(field, args, return_none=False):
    if field not in args:
        if not return_none:
            abort(Response("'{}' not in args".format(field), 400))
        else:
            return None

    return args[field]

@app.route("/sample", methods=["POST"])
def sample():
    model_mko = get_input("model_mko", request.args)
    xs = get_input("x", request.args)
    samples = get_input("samples", request.args)

    try:
        xs = list(json.loads(xs))
    except Exception as e:
        return Response("Format 'x' as array of floats")

    try:
        ys = MKO.from_b64str(model_mko).make_inference(xs, samples).tolist()
    except MKOTypeException as e:
        return Response(str(e), 400)
    except InputException as e:
        return Response(str(e), 400)
    except Exception as e:
        return Response(traceback.format_exc(), 500)

    response_text = {
        "y": ys
    }
    
    return Response(json.dumps(response_text), 200)