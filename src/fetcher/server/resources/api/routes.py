from flask import request
from flask.wrappers import Response
from werkzeug.exceptions import BadRequest
import json

from server.resources.api import bp
import server.smip as smip

@bp.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "Hello World!"

@bp.route("/validateAttributeById", methods=['GET'])
def validate_attribute_by_id():
  request_data = json.loads(request.args.get('query'))  # type: ignore
  try:
    smip_url = request_data.get('url')
    smip_token = request_data.get('smip_token')
    attrib_id = request_data.get('attrib_id')
    attrib_description = smip.get_equipment_description(smip_url, smip_token, attrib_id)
    if attrib_description['attribute'] == None:
      return Response("No such attribute", status=422)
    else:
      return Response("Successfully validated attribute id: {}".format(attrib_id), status=200)
  except smip.GraphQLAuthenticationError as err:
    return Response("Authorization failed", status=500)
  except Exception as err:
    return Response("SMIP returned {}".format(err), status=500)

@bp.route("/rawDataById", methods=['GET'])
def raw_data_by_id():
  request_data = json.loads(request.args.get('query'))  # type: ignore
  try:
    smip_url = request_data.get('url')
    smip_token = request_data.get('smip_token')
    attrib_id = request_data.get('attrib_id')
    csv_data = smip.get_equipment_description(smip_url, smip_token, attrib_id)
    return Response(csv_data, status=200)
  except smip.GraphQLAuthenticationError as err:
    return Response("Authorization failed", 500)
  except Exception as err:
    raise BadRequest("SMIP returned {}".format(err))

@bp.route("/timeseriesById")
def timeseries_by_id():
  request_data = json.loads(request.args.get('query'))  # type: ignore
  try:
    smip_url = request_data.get('url')
    smip_token = request_data.get('smip_token')
    attrib_id = request_data.get('attrib_id')
    start_time = request_data.get('start_time', None)
    end_time = request_data.get('end_time', None)
    csv_data = smip.get_timeseries(smip_url, smip_token,
      attrib_id, start_time, end_time, max_samples=0)
    return Response(csv_data, status=200)
  except smip.GraphQLAuthenticationError as err:
    return Response("Authorization failed", 500)
  except Exception as err:
    return("Bad Request. SMIP returned {}".format(err), 400)

@bp.route("/timeseriesArrayById")
def timeseries_array_by_id():
  request_data = json.loads(request.args.get('query'))  # type: ignore
  try:
    smip_url = request_data.get('url')
    smip_token = request_data.get('smip_token')
    attrib_id_list = request_data.get('attrib_id_list')
    period = request_data.get('period')
    start_time = request_data.get('start_time', None)
    end_time = request_data.get('end_time', None)
    csv_data = smip.get_timeseries_array(smip_url, smip_token,
      attrib_id_list, start_time, end_time, period)
    return Response(csv_data, status=200)
  except smip.GraphQLAuthenticationError as err:
    return Response("Authorization failed", 500)
  except Exception as err:
    raise BadRequest("SMIP returned {}".format(err))
