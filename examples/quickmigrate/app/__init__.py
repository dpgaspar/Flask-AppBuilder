import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_migrate import Migrate

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
migrate = Migrate(app, db)
appbuilder = AppBuilder(app, db.session)

from . import models, views  # noqa
