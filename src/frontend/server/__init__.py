import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'server.config.DevelopmentConfiguration')
app.config.from_object(app_settings)
db = SQLAlchemy(app)
from server import routes, models
from server.Logger.models import Event

db.create_all()

app.config['SERVER_SESSION'] = os.urandom(24)

print("Starting with server_secret: '{}'".format(app.config.get('SERVER_SECRET')))
from server.Resources.Admin.routes import AdminResource
app.register_blueprint(AdminResource)

from server.Resources.Analyze.routes import AnalyzeResource
app.register_blueprint(AnalyzeResource)

from server.Resources.Infer.routes import InferResource
app.register_blueprint(InferResource)

from server.Resources.Logging.routes import LoggingResource
app.register_blueprint(LoggingResource)

from server.Resources.ResultCache.routes import RCResource
app.register_blueprint(RCResource)

from server.Resources.Train.routes import TrainResource
app.register_blueprint(TrainResource)

from server.Resources.User.routes import UserResource
app.register_blueprint(UserResource)

## Clear logs and log a server startup
Event.query.delete()
Event("SERVER", "Server started").logit()
Event("SERVER", "Unique session ID: {}".format(app.config['SERVER_SESSION']) ).logit()