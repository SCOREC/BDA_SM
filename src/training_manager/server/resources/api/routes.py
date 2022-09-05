from flask import request
from flask.wrappers import Response
from tempfile import NamedTemporaryFile
from subprocess import Popen
import json

from server.resources.api import bp
import server.curator
import server.trainer


@bp.route("/helloWorld", methods=["GET"])
def imAlive():
  return Response("Hello World!", 200)

# username: username of user
# model_name: name of the model to be created
@bp.route("/create_MKO", methods=["POST"])
def create_MKO():
  try:
    data = request.data
    data = json.loads(data)['data']
    model_name = data.get('model_name')
    username =  data.get('username')
    claim_check = server.curator.create_mko(model_name, username)
  except Exception as err:
    print("Bad request: ",request.data)
    return Response("Badly formed request: {}".format(err), 400)

  return ({"claim_check": claim_check}, 200)

@bp.route("/fill_mko", methods=["POST"])
def fill_data():
  try:
    data = request.data
    data = json.loads(data)['data']
    username = data.get("username")
    model_name = data.get("model_name")
    dataspec = data.get('dataspec')
    topology = data.get("topology", list([]))
    hypers = data.get('hyper_parameters', {})
    mko = data.get('mkodata')
    claim_check = server.curator.fill_mko(username, model_name, mko, dataspec, topology, hypers)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)

  return ({"claim_check": claim_check}, 200)

@bp.route("/train", methods=["POST"])
def train():
  try:
    data = request.data
    data = json.loads(data)['data']
    username = data.get("username")
    model_name = data.get("model_name")
    mko = data.get('mkodata')
    smip_token = data.get('smip_auth').get('token')
    smip_url = data.get('smip_auth').get('url')
    claim_check = server.trainer.train_mko(username, model_name, mko, smip_token, smip_url)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)

  return ({"claim_check": claim_check}, 200)