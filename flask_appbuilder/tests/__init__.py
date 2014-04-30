import logging
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask.ext.appbuilder.models.mixins import BaseMixin
from flask.ext.appbuilder import Base
from flask.ext.appbuilder.baseapp import BaseApp

from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)




def setup():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'thisismyscretkey'
    app.config['WTF_CSRF_ENABLED'] = False

    db = SQLAlchemy(app)

    return db, app
