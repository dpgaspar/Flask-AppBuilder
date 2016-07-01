import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.menu import Menu
from .sec import MySecurityManager
from .indexview import MyIndexView
from sqlalchemy.engine import Engine
from sqlalchemy import event

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')
db = SQLA(app)


appbuilder = AppBuilder(app, db.session, indexview=MyIndexView,
                        menu=Menu(reverse=False), security_manager_class=MySecurityManager)

"""
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from app import views

