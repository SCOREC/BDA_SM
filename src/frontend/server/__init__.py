import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app_settings = os.getenv('APP_SETTINGS', 'frontend.server.config.DevelopmentConfig')
app.config.from_object(app_settings)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from frontend.server import routes, models

from frontend.server.Resources.Admin.routes import AdminResource
app.register_blueprint(AdminResource)

from frontend.server.Resources.User.routes import UserResource
app.register_blueprint(UserResource)