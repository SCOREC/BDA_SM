
from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.Resources.util import forward_request

InferResource = Blueprint('Infer', __name__, url_prefix='/Infer')
inference_manager_host = str(app.config.get('INFERENCE_MANAGER_HOST'))

@InferResource.route('/sample', methods=['POST'])
@initialized(True)
@require_access(['infer'])
def infer_sample():
    return forward_request(target_url=inference_manager_host +
      "/sample")