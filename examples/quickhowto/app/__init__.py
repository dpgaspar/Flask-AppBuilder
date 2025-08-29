import logging

from flask import Flask
from .views import ContactModelView, ContactTimeChartView, GroupModelView
from .extensions import appbuilder, db
from .utils import fill_gender


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        db.init_app(app)
        appbuilder.init_app(app, db.session)
        db.create_all()
        fill_gender()
        appbuilder.add_view(
            GroupModelView,
            "List Groups",
            icon="fa-folder-open-o",
            category="Contacts",
            category_icon="fa-envelope",
        )
        appbuilder.add_view(
            ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
        )
        appbuilder.add_separator("Contacts")
        appbuilder.add_view(
            ContactTimeChartView,
            "Contacts Birth Chart",
            icon="fa-dashboard",
            category="Contacts",
        )
    return app
