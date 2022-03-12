from flask import Blueprint

from server import app
from server.wrappers import require_access, initialized
from server.Resources.util import forward_request

TrainResource = Blueprint('Train', __name__, url_prefix='/Train')
training_manager_host = str(app.config.get('TRAINING_MANAGER_HOST'))

@TrainResource.route('/create_MKO', methods=['POST'])
@initialized(True)
@require_access('train')
def train_create_MKO():
    return forward_request(target_url=training_manager_host +
      "/create_MKO")

@TrainResource.route('/add_component', methods=['POST'])
@initialized(True)
@require_access('train')
def train_add_component():
    return forward_request(target_url=training_manager_host +
      "/add_component")

@TrainResource.route('/train', methods=['POST'])
@initialized(True)
@require_access('train')
def train_train():
    return forward_request(target_url=training_manager_host +
      "/train")

