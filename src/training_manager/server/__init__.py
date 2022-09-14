import os
from flask import Flask, Blueprint, request

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'server.config.ProductionConfiguration')
app.config.from_object(app_settings)

import server.resources.api
app.register_blueprint(server.resources.api.bp, url_prefix='/api')

@app.route('/helloWorld', methods = ['GET'])
def imAlive():
    request_data = request.args.get('query')  # type: ignore
    return "Hello World!"