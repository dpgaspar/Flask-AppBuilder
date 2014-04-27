from nose.tools import eq_, ok_, raises

import os
import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.appbuilder.baseapp import BaseApp

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
"""
    Your database connection String
"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['CSRF_ENABLED'] = True

"""
    Secret key for authentication cookies
"""
app.config['SECRET_KEY'] = 'thisismyscretkey'
"""
    The Flask-SQLAlchemy object initialization with the SQLALCHEMY_DATABASE_URI string you have setup
"""
db = SQLAlchemy(app)

"""
    The Base Flask-AppBuilder object initialization
"""
genapp = BaseApp(app, db)
