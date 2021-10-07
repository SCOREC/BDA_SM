from flask import Flask
from .file_daemon import FileHandler
from .config import config

app = Flask(__name__)
from . import routes

