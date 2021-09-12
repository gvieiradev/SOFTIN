from flask import Flask
from .auth import auth
from flask_bootstrap import Bootstrap
from .config import Config



def Create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    app.config.from_object(config)
    app.register_blueprint(auth)
    return app