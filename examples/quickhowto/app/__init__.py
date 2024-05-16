from flask import Flask

from .views import ContactModelView, ContactTimeChartView, GroupModelView
from .extensions import appbuilder, db
from .utils import fill_gender


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    with app.app_context():
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
