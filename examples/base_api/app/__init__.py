from flask import Flask

from .api import ExampleApi
from .extensions import  appbuilder, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    with app.app_context():
        appbuilder.init_app(app, db.session)
        appbuilder.add_api(ExampleApi)
    return app
