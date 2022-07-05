import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


def create_app(config):
    app = Flask(__name__)
    db = SQLA()
    appbuilder = AppBuilder()
    with app.app_context():
        app.config.from_object(config)
        db.init_app(app)
        appbuilder.init_app(app, db.session)

        from .views import ContactModelView, GroupModelView, fill_gender

        appbuilder.add_view(
            ContactModelView,
            "List Contacts",
            icon="fa-envelope",
            category="Contacts",
            category_icon="fa-envelope",
        )

        appbuilder.add_view(
            GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts"
        )

        db.create_all()
        appbuilder.post_init()
        fill_gender()
    return app
