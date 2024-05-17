from flask import Flask

from .api import GreetingApi, ContactModelApi, GroupModelApi, ModelOMParentApi
from .extensions import  appbuilder, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    with app.app_context():
        db.create_all()
        appbuilder.init_app(app, db.session)
        appbuilder.add_api(GreetingApi)
        appbuilder.add_api(ContactModelApi)
        appbuilder.add_api(GroupModelApi)
        appbuilder.add_api(ModelOMParentApi)
    return app
