import os
from flask import Flask
from config import Config
from api.endpoints import api as api_bp

def configure_app(app):
    @app.route('/fetcher_home')
    def fetcher_home():
        return 'This is fetcher home!'

    app.register_blueprint(api_bp, url_prefix='/api')
    
    from  . import auth
    app.register_blueprint(auth.bp)
    return fetcher_home

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    configure_app(app)

    return app

app = create_app()