from flask import request
from flask.wrappers import Response
from tempfile import NamedTemporaryFile
from subprocess import Popen
import server.trainer
import json

from server.resources.api import bp


@bp.route("/helloWorld", methods=["GET"])
def imAlive():
  return Response("Hello World!", 200)

# username: username of user
# model_name: name of the model to be created
@bp.route("/create_MKO", methods=["POST"])
def create_MKO():
  try:
    model_name = request.values["model_name"]
    username = request.values["username"]
    claim_check = server.trainer.create_mko(model_name, username)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)

  return ({"claim_check": claim_check}, 200)

# result_chache_URI: URI of result cache
# username: username of user
# claim_check: specified claim_check to post to
# type: type of portion to add (eg. data, hyperparmams, etc.)
# to_add: json string of portion to add
# model_MKO: json string of mko
# merges the to_add json with the model_MKO under the type field
@bp.route("/fill_mko", methods=["POST"])
def fill_data():
  try:
    username = request.values.get("username")
    model_name = request.values.get("model_name")
    query = json.loads(request.values.get("query"))
    dataspec = query['data']
    topology = query.get('topology', list([]))
    hypers = query.get('hyper_parameters', {})
    claim_check = server.trainer.fill_mko(username, model_name, dataspec, topology, hypers)
  except Exception as err:
    return Response("Badly formed request: {}".format(err), 400)

  return ({"claim_check": claim_check}, 200)