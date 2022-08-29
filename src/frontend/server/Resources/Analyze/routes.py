from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.Resources.util import forward_request

AnalyzeResource = Blueprint('Analyze', __name__, url_prefix='/Analyze')
inference_manager_host = str(app.config.get('INFERENCE_MANAGER_HOST'))

@AnalyzeResource.route('/stat', methods=['POST'])
@initialized(True)
@require_access(['Analyze'])
def Analyze_sample():
    return forward_request(target_url=inference_manager_host +
      "/stat")

@AnalyzeResource.route('/integrate', methods=['POST'])
@initialized(True)
@require_access(['Analyze'])
def Analyze_integrate():
    return forward_request(target_url=inference_manager_host +
      "/integrate")