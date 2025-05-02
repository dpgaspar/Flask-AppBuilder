import logging

from flask import Flask
from flask_appbuilder.extensions import db
from .views import ContactModelView, ContactTimeChartView, GroupModelView
from .extensions import appbuilder
from .utils import fill_gender


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)
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
