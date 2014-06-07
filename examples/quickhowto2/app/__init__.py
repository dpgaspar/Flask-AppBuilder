import os
import logging
from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
from sqlalchemy.engine import Engine
from sqlalchemy import event

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

db = SQLA()
appbuilder = AppBuilder()


"""
Only include this for SQLLite constraints

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    

from app import views

def create_app(config='config'):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    with app.app_context():
        views.fill_gender()
        appbuilder.init_app(app, db.session)
        appbuilder.security_cleanup()
    return app
