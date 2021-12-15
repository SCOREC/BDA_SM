from .file_daemon import FileHandler
from .config import config
from flask import Flask

app = Flask(__name__)

from . import routes
