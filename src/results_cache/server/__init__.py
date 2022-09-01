import os
from flask import Flask, Blueprint, request
import server.file_daemon

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'server.config.TestingConfiguration')
app.config.from_object(app_settings)

import server.resources.api
app.register_blueprint(server.resources.api.bp, url_prefix='/api')

server.file_daemon.file_handler = server.file_daemon.FileHandler(
    app.config['MIN_EXPIRY_TIME'], app.config['MAX_EXPIRY_TIME'],
    app.config['RATE_AVERAGE_WINDOW'], app.config['DIRECTORY']
    )


@app.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "Hello World!"