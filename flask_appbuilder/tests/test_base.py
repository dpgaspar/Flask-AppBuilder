from nose.tools import eq_, ok_, raises

import os
import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.appbuilder.baseapp import BaseApp

def setup():

    basedir = os.path.abspath(os.path.dirname(__file__))
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = 'thisismyscretkey'
    db = SQLAlchemy(app)
    return db, app


def test_base_init():
    db, app = setup()
    genapp = BaseApp(app, db)
    ok_(len(genapp.baseviews) > 0) # current minimal views are 11


