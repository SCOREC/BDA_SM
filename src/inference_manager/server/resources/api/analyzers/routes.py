from flask import Blueprint
from flask import request, abort
from flask.wrappers import Response

from subprocess import Popen, PIPE, STDOUT

from server.config import AnalyzersConfig as cfg
from server.resources.util import forward_request

AnalyzersResource = Blueprint('Analyzers', __name__)
sampler_base_url = str(cfg.SAMPLER_BASE_URL).rstrip('/ ')
executable_path = "python -m analyzers.src.analyzers".split(" ")

@AnalyzersResource.route('/statistics', methods=['POST'])
def statistics():
    return forward_request(target_url=sampler_base_url + "/api/sampler")