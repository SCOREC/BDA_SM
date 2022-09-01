from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.Resources.util import forward_request

RCResource = Blueprint('ResultCache', __name__, url_prefix='/Results')
results_cache_host = str(app.config.get('RESULTS_CACHE_BASE_URL')).rstrip('/ ')

@RCResource.route('/get_result', methods=['GET'])
@initialized(True)
@require_access(['train', 'infer'])
def get_result():
    return forward_request(target_url=results_cache_host + "/api/get_result")

@RCResource.route('/get_status', methods=['GET'])
@initialized(True)
@require_access(['train', 'infer'])
def get_status():
    return forward_request(target_url=results_cache_host + "/api/get_status")

@RCResource.route('/get_eta', methods=['GET'])
@initialized(True)
@require_access(['train', 'infer'])
def get_eta():
    return forward_request(target_url=results_cache_host + "/api/get_eta")