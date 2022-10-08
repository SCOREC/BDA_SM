from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.util import forward_request

AnalyzeResource = Blueprint('Analyze', __name__, url_prefix='/Analyze')
inference_manager_host = str(app.config.get('INFERENCE_MANAGER_BASE_URL'))

@AnalyzeResource.route('/cloudplot', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_cloudplot():
    return forward_request(target_url=inference_manager_host.rstrip("/ ") +
      "/api/analyze/cloudplot")

@AnalyzeResource.route('/histogram', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_histogram():
    return forward_request(target_url=inference_manager_host.rstrip("/ ") +
      "/api/analyze/histogram")

@AnalyzeResource.route('/history', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_history():
    return forward_request(target_url=inference_manager_host.rstrip("/ ") +
      "/api/analyze/history")

@AnalyzeResource.route('/integrate', methods=['POST'])
@initialized(True)
@require_access(['analyze'])
def Analyze_integrate():
    return forward_request(target_url=inference_manager_host +
      "/api/analyze/integrate")