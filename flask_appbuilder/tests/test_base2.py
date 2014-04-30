from nose.tools import eq_, ok_, raises
import unittest
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


import logging

DEFAULT_INDEX_STRING = 'Welcome'

log = logging.getLogger(__name__)


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
        self.app.config['CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'thisismyscretkey'
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.db = SQLAlchemy(self.app)


    def tearDown(self):
        pass


    def test_empty_db(self):
        pass
        """
        client = self.app.test_client()

        rv = client.get('/')
        ok_(len(baseapp.baseviews) > 9) # current minimal views are 11
        """