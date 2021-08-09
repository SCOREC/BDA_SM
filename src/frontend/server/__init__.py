import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'frontend.server.config.DevelopmentConfig')
app.config.from_object(app_settings)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from frontend.server import routes
from frontend.server.Logger.models import Event

Event.query.delete()
ev = Event("SERVER", "Server started")
db.session.add(ev)
app.config['SERVER_SESSION'] = os.urandom(24)
ev = Event("SERVER", "Unique session ID: {}".format(app.config['SERVER_SESSION']) )
db.session.commit()

print("Starting with server_secret: '{}'".format(app.config.get('SERVER_SECRET')))
from frontend.server.Resources.Admin.routes import AdminResource
app.register_blueprint(AdminResource)

from frontend.server.Resources.Logging.routes import LoggingResource
app.register_blueprint(LoggingResource)

from frontend.server.Resources.User.routes import UserResource
app.register_blueprint(UserResource)