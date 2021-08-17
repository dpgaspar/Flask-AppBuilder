import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from .Dashboard import Dash_App1, Dash_App2

"""
 Logging configuration
"""
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)
app = Dash_App1.Add_Dash(app, appbuilder)
app = Dash_App2.Add_Dash(app, appbuilder)

from . import views  # noqa
