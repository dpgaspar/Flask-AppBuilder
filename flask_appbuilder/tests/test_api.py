import unittest
import os
import string
import random
import datetime
import json
import logging

from nose.tools import eq_, ok_

log = logging.getLogger(__name__)
from flask_appbuilder import SQLA
from .sqla.models import Model1, insert_data

MODEL1_DATA_SIZE = 10

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.models.sqla.interface import SQLAInterface
        from flask_appbuilder.api import ModelApi

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self.app.config['CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'thisismyscretkey'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        # Create models and insert data
        insert_data(self.db.session, Model1, MODEL1_DATA_SIZE)

        class Model1Api(ModelApi):
            datamodel = SQLAInterface(Model1)
            list_columns = ['field_integer', 'field_float', 'field_string', 'field_date']
            description_columns = {
                'field_integer': 'Field Integer',
                'field_float': 'Field Float',
                'field_string': 'Field String'
            }

        self.model1api = Model1Api
        self.appbuilder.add_view_no_menu(Model1Api)


    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_get_item(self):
        """
            REST Api: Test get item
        """
        client = self.app.test_client()

        for i in range(1, MODEL1_DATA_SIZE):
            rv = client.get('api/v1/model1api/{}/'.format(i))
            data = json.loads(rv.data.decode('utf-8'))
            self.assert_get_item(rv, data, i-1)

    def assert_get_item(self, rv, data, value):
        log.info("assert_get_item: {} {}".format(data, value))
        # test result
        eq_(data['result'], {'field_date':None,
                             'field_float':float(value),
                             'field_integer':value,
                             'field_string':"test{}".format(value)})
        # test descriptions
        eq_(data['description_columns'], self.model1api.description_columns)
        # test labels
        eq_(data['label_columns'], {'field_date':'Field Date',
                                    'field_float':'Field Float',
                                    'field_integer':'Field Integer',
                                    'field_string':'Field String',
                                    'id':'Id'})
        eq_(rv.status_code, 200)

    def test_get_list(self):
        """
            REST Api: Test get list
        """
        client = self.app.test_client()

        rv = client.get('api/v1/model1api/')
        data = json.loads(rv.data.decode('utf-8'))
        for i in range(1, MODEL1_DATA_SIZE):
            self.assert_get_list(rv, data['result'][i-1], i-1)

    def assert_get_list(self, rv, data, value):
        log.info("assert_get_list: {} {}".format(data, value))
        # test result
        eq_(data, {'field_date':None,
                             'field_float':float(value),
                             'field_integer':value,
                             'field_string':"test{}".format(value)})
        eq_(rv.status_code, 200)


