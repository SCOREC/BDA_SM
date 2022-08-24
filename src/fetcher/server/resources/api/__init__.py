from flask import Blueprint
from server import app

bp = Blueprint('api',__name__)
from server.resources.api import routes