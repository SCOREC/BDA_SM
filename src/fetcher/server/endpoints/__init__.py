from flask import Blueprint, url_for

api = Blueprint('gettimeseries',__name__)
from server.endpoints import routes