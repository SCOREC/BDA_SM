from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.util import forward_request

TrainResource = Blueprint('Train', __name__, url_prefix='/Train')
training_manager_host = str(app.config.get('TRAINING_MANAGER_BASE_URL')).rstrip('/ ')

@TrainResource.route('/create_MKO', methods=['POST'])
@initialized(True)
@require_access(['train'])
def train_create_MKO():
    return forward_request(target_url=training_manager_host +
      "/api/create_MKO")

@TrainResource.route('/fill_mko', methods=['POST'])
@initialized(True)
@require_access(['train'])
def train_add_component():
    return forward_request(target_url=training_manager_host +
      "/api/fill_mko")

@TrainResource.route('/train', methods=['POST'])
@initialized(True)
@require_access(['train'])
def train_train():
    return forward_request(target_url=training_manager_host +
      "/api/train")

@TrainResource.route('/trainCalibrate', methods=['POST'])
@initialized(True)
@require_access(['train'])
def train_calibrate():
    return forward_request(target_url=training_manager_host +
      "/api/trainCalibrate")

@TrainResource.route('/describe_mko', methods=['POST'])
@initialized(True)
@require_access(['train'])
def train_describe():
    return forward_request(target_url=training_manager_host +
      "/api/describe_mko")