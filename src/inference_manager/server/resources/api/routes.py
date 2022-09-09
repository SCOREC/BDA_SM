from flask import Blueprint
from flask import request, abort
from flask.wrappers import Response
from subprocess import Popen, PIPE, STDOUT
import json
from server.config import AnalyzersConfig as cfg
from server.resources.util import forward_request

IMResource = Blueprint('Sampler', __name__)
sampler_base_url = str(cfg.SAMPLER_BASE_URL).rstrip('/ ')

@IMResource.route('/sample', methods=['POST'])
def sample():
    return forward_request(target_url=sampler_base_url + "/api/sample")