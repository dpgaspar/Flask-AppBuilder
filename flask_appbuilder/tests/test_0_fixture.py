import os
import unittest

from flask_appbuilder import SQLA

from .sqla.models import insert_data


MODEL1_DATA_SIZE = 30


class TestData(unittest.TestCase):

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object('flask_appbuilder.tests.config_api')
        self.db = SQLA(self.app)

    def test_data(self):
        insert_data(self.db.session, MODEL1_DATA_SIZE)
