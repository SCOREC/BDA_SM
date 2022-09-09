from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.util import forward_request

AnalyzeResource = Blueprint('Analyze', __name__, url_prefix='/Analyze')
inference_manager_host = str(app.config.get('INFERENCE_MANAGER_BASE_URL'))

@AnalyzeResource.route('/histogram', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_sample():
    return forward_request(target_url=inference_manager_host.rstrip("/ ") +
      "/api/analyze/histogram")

@AnalyzeResource.route('/integrate', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_integrate():
    return forward_request(target_url=inference_manager_host +
      "/integrate")