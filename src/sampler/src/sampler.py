import sys
from flask import Flask, Blueprint
from mko import MKO
from network.model import Model
from sampler import config, routes

app = Flask(__name__)
app.config.from_object(config.BaseConfig)

app.run(host='127.0.0.1', port=8181)