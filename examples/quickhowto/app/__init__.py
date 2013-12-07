import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask.ext.babel import Babel
from config import basedir

"""
# Include this for Flask-AppBuilder 0.2.X

from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

"""

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
babel = Babel(app)

"""
# Include this for Flask-AppBuilder 0.2.X

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))
"""


"""
Only include this for SQLLite constraints
"""
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
        Will force sqllite contraint foreign keys
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    

from app import views

