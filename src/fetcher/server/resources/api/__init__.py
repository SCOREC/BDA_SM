from flask import Blueprint

bp = Blueprint('api',__name__)
from server.resources.api import routes