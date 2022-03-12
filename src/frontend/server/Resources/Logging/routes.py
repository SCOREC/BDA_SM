# frontend/server/Resources/Logging/routes.py
from flask import Blueprint
from flask import render_template, jsonify
from flask import request

from server.errors import AuthenticationError
from server.wrappers import require_access, initialized
from server.Logger.models import Event

LoggingResource = Blueprint('Logging', __name__, url_prefix='/Logging', template_folder='templates')

@LoggingResource.route('/viewall', methods=['POST'])
@initialized(True)
@require_access('logs')
def viewall():
  events = Event.query.all()

  return render_template('Logging/viewer.html', events=events, title='All logs')