# -*- coding: utf-8 -*-
import logging

from flask import Flask
from fab.flask_appbuilder import AppBuilder
from fab.flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_mongoengine import MongoEngine
from .security import MySecurityManager

from fab.flask_appbuilder.security.mongoengine.models import User

from views import add_views
from setup import ez_setup

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')
dbmongo = MongoEngine(app)
appbuilder = AppBuilder(app, security_manager_class=MySecurityManager)

# initialize mongodb if needed
ez_setup(appbuilder, User)

# import views
add_views(appbuilder)

