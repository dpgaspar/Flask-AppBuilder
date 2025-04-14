from flask import Flask

from flask_appbuilder.extensions import db
from .api import GreetingApi, ContactModelApi, GroupModelApi, ModelOMParentApi, ContactGroupModelView, ContactGroupTagModelView
from .extensions import appbuilder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)
        db.create_all()
        appbuilder.add_api(GreetingApi)
        appbuilder.add_api(ContactModelApi)
        appbuilder.add_api(GroupModelApi)
        appbuilder.add_api(ModelOMParentApi)
        appbuilder.add_view(
            ContactGroupModelView,
            "List Contact Groups",
            icon="fa-folder-open-o",
            category="Contacts",
            category_icon="fa-envelope",
        )
        appbuilder.add_view(
            ContactGroupTagModelView,
            "List Contact Group Tags",
            icon="fa-folder-open-o",
            category="Contacts",
            category_icon="fa-envelope",
        )
    return app
