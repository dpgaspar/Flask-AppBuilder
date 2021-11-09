import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.menu import Menu

from .indexview import MyIndexView
from .sec import MySecurityManager

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)

appbuilder = AppBuilder(
    app,
    db.session,
    indexview=MyIndexView,
    menu=Menu(reverse=False),
    security_manager_class=MySecurityManager,
)

from . import views  # noqa
