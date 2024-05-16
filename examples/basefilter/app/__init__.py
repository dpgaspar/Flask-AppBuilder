from flask import Flask

from .views import ContactModelView, GroupModelView
from .extensions import app, appbuilder, db


def create_app() -> Flask:
    appbuilder.init_app(app, db.session)
    db.create_all()
    appbuilder.add_view(
        GroupModelView,
        "List Groups",
        icon="fa-folder-open-o",
        category="Contacts",
        category_icon="fa-envelope",
    )
    appbuilder.add_separator("Contacts")
    appbuilder.add_view(
        ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
    )
    return app
