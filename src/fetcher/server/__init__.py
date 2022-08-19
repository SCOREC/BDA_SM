import os
from flask import Flask

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'server.config.DevelopmentConfig')
app.config.from_object(app_settings)

from server import routes

import server.resources.api
app.register_blueprint(server.resources.api.bp, url_prefix='/api')
