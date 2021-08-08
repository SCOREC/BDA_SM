# frontend/Tests/base.py

from flask_testing import TestCase
from frontend.server import app, db
from frontend.Tests import Config

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object(Config)
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()