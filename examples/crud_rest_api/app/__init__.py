from flask import Flask
from .api import GreetingApi, ContactModelApi, GroupModelApi, ModelOMParentApi, ContactGroupModelView, ContactGroupTagModelView
from .extensions import appbuilder, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        db.init_app(app)
        appbuilder.init_app(app, db.session)
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


# For backward compatibility
app = create_app()
