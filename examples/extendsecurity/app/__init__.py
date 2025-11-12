import logging

from flask import Flask

from .extensions import appbuilder
from .views import ContactModelView, GroupModelView, CompanyModelView


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


def create_app():
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object("config")
        appbuilder.init_app(app)
        appbuilder.add_view(
            ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
        )
        appbuilder.add_separator("Contacts")
        appbuilder.add_view(
            GroupModelView,
            "List Groups",
            icon="fa-folder-open-o",
            category="Contacts",
            category_icon="fa-envelope",
        )
        appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o")

    return app
