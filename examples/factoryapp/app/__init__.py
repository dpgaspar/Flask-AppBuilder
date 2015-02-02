import logging
from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
#from sqlalchemy.engine import Engine
#from sqlalchemy import event

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

db = SQLA()
appbuilder = AppBuilder()

from app import views


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    with app.app_context():
        appbuilder.init_app(app, db.session)
        db.create_all(app=app)
        views.fill_gender()
    return app




