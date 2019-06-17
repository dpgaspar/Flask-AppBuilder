import logging

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_mongoengine import MongoEngine


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
dbmongo = MongoEngine(app)
appbuilder = AppBuilder(app, security_manager_class=SecurityManager)

from . import models, views  # noqa
