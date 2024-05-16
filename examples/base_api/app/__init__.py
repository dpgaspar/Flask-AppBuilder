from flask import Flask

from .api import ExampleApi
from .extensions import app, appbuilder, db


def create_app() -> Flask:
    appbuilder.init_app(app, db.session)
    appbuilder.add_api(ExampleApi)
    return app
