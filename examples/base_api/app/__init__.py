from flask import Flask
from .api import ExampleApi
from .extensions import appbuilder, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        db.init_app(app)
        appbuilder.init_app(app, db.session)
        appbuilder.add_api(ExampleApi)
    return app


# For backward compatibility
app = create_app()
