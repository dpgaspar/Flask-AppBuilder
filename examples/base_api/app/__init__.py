from flask import Flask

from .api import ExampleApi
from .extensions import appbuilder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)
        appbuilder.add_api(ExampleApi)
    return app
