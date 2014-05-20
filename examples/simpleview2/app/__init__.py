import logging
from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
from sqlalchemy.engine import Engine
from sqlalchemy import event

"""
 Logging configuration
"""
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__)
app.config.from_object('config')
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

from app import views

