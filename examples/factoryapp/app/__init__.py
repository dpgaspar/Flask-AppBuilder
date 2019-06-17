import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

db = SQLA()
appbuilder = AppBuilder()


def create_app(config):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        db.init_app(app)
        appbuilder.init_app(app, db.session)
        from . import views  # noqa

        db.create_all()
        appbuilder.post_init()
        views.fill_gender()
    return app
