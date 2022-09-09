import os
from flask import Flask, Blueprint, request

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'server.config.DevelopmentConfig')
app.config.from_object(app_settings)

import server.resources.api
app.register_blueprint(server.resources.api.bp, url_prefix='/api')
import server.resources.api.analyzers
app.register_blueprint(server.resources.api.analyzers.bp, url_prefix='/api/analyze')

@app.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "Hello World!"