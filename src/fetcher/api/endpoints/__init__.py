from flask import Blueprint, url_for

api = Blueprint('gettimeseries',__name__)
from api.endpoints import routes