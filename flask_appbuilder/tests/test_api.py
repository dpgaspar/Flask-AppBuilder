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
        self.app.config['SECRET_KEY'] = 'thisismyscretkey'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session, update_perms=False)
        # Create models and insert data
        insert_data(self.db.session, Model1, MODEL1_DATA_SIZE)

        class Model1Api(ModelApi):
            datamodel = SQLAInterface(Model1)
            list_columns = [
                'field_integer',
                'field_float',
                'field_string',
                'field_date'
            ]
            description_columns = {
                'field_integer': 'Field Integer',
                'field_float': 'Field Float',
                'field_string': 'Field String'
            }

        class Model1FuncApi(ModelApi):
            datamodel = SQLAInterface(Model1)
            list_columns = [
                'field_integer',
                'field_float',
                'field_string',
                'field_date',
                'full_concat'
            ]
            description_columns = {
                'field_integer': 'Field Integer',
                'field_float': 'Field Float',
                'field_string': 'Field String'
            }

        self.model1api = Model1Api
        self.appbuilder.add_view_no_menu(Model1Api)
        self.model1funcapi = Model1Api
        self.appbuilder.add_view_no_menu(Model1FuncApi)

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
            eq_(rv.status_code, 200)
            self.assert_get_item(rv, data, i - 1)

    def assert_get_item(self, rv, data, value):
        eq_(data['result'], {
            'field_date': None,
            'field_float': float(value),
            'field_integer': value,
            'field_string': "test{}".format(value)
        })
        # test descriptions
        eq_(data['description_columns'], self.model1api.description_columns)
        # test labels
        eq_(data['label_columns'], {
            'field_date': 'Field Date',
            'field_float': 'Field Float',
            'field_integer': 'Field Integer',
            'field_string': 'Field String'
        })
        eq_(rv.status_code, 200)

    def test_get_item_select_cols(self):
        """
            REST Api: Test get item with select columns
        """
        client = self.app.test_client()

        for i in range(1, MODEL1_DATA_SIZE):
            rv = client.get('api/v1/model1api/{}/?_c_=field_integer'.format(i))
            data = json.loads(rv.data.decode('utf-8'))
            eq_(data['result'], {'field_integer': i - 1})
            eq_(data['description_columns'], {
                'field_integer': 'Field Integer'
            })
            eq_(data['label_columns'], {
                'field_integer': 'Field Integer'
            })
            eq_(rv.status_code, 200)

    def test_get_item_not_found(self):
        """
            REST Api: Test get item not found
        """
        client = self.app.test_client()
        pk = 11
        rv = client.get('api/v1/model1api/{}/'.format(pk))
        eq_(rv.status_code, 404)

    def test_get_list(self):
        """
            REST Api: Test get list
        """
        client = self.app.test_client()

        rv = client.get('api/v1/model1api/')
        data = json.loads(rv.data.decode('utf-8'))
        # Tests count property
        eq_(data['count'], MODEL1_DATA_SIZE)
        # Tests data result default page size
        eq_(len(data['result']), self.model1api.page_size)
        for i in range(1, MODEL1_DATA_SIZE):
            self.assert_get_list(rv, data['result'][i - 1], i - 1)

    @staticmethod
    def assert_get_list(rv, data, value):
        log.info("assert_get_list: {} {}".format(data, value))
        # test result
        eq_(data, {
            'field_date': None,
            'field_float': float(value),
            'field_integer': value,
            'field_string': "test{}".format(value)
        })
        eq_(rv.status_code, 200)

    def test_get_list_order(self):
        """
            REST Api: Test get list order params
        """
        client = self.app.test_client()

        # test string order asc
        rv = client.get('api/v1/model1api/?_o_=field_string:asc')
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_date': None,
            'field_float': 0.0,
            'field_integer': 0,
            'field_string': "test0"
        })
        eq_(rv.status_code, 200)
        # test string order desc
        rv = client.get('api/v1/model1api/?_o_=field_string:desc')
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_date': None,
            'field_float': float(MODEL1_DATA_SIZE - 1),
            'field_integer': MODEL1_DATA_SIZE - 1,
            'field_string': "test{}".format(MODEL1_DATA_SIZE - 1)
        })
        eq_(rv.status_code, 200)

    def test_get_list_page(self):
        """
            REST Api: Test get list page params
        """
        page_size = 5
        client = self.app.test_client()

        # test page zero
        uri = 'api/v1/model1api/?_p_={}:0&_o_=field_integer:asc'.format(page_size)
        rv = client.get(uri)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_date': None,
            'field_float': 0.0,
            'field_integer': 0,
            'field_string': "test0"
        })
        eq_(rv.status_code, 200)
        eq_(len(data['result']), page_size)
        # test page zero
        uri = 'api/v1/model1api/?_p_={}:1&_o_=field_integer:asc'.format(page_size)
        rv = client.get(uri)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_date': None,
            'field_float': float(page_size),
            'field_integer': page_size,
            'field_string': "test{}".format(page_size)
        })
        eq_(rv.status_code, 200)
        eq_(len(data['result']), page_size)

    def test_get_list_filters(self):
        """
            REST Api: Test get list filter params
        """
        client = self.app.test_client()
        filter_value = 5
        # test string order asc
        uri = 'api/v1/model1api/?_f_0=field_integer:gt:{}&_o_=field_integer:asc'.format(filter_value)
        rv = client.get(uri)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_date': None,
            'field_float': float(filter_value + 1),
            'field_integer': filter_value + 1,
            'field_string': "test{}".format(filter_value + 1)
        })
        eq_(rv.status_code, 200)

    def test_get_list_select_cols(self):
        """
            REST Api: Test get list with selected columns
        """
        client = self.app.test_client()
        uri = 'api/v1/model1api/?_c_=field_integer&_o_=field_integer:asc'
        rv = client.get(uri)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['result'][0], {
            'field_integer': 0,
        })
        eq_(data['label_columns'], {
            'field_integer': 'Field Integer'
        })
        eq_(data['description_columns'], {
            'field_integer': 'Field Integer'
        })
        eq_(data['list_columns'], [
            'field_integer'
        ])
        eq_(rv.status_code, 200)

    def test_info_filters(self):
        """
            REST Api: Test info filters
        """
        client = self.app.test_client()
        uri = 'api/v1/model1api/info'
        rv = client.get(uri)
        data = json.loads(rv.data.decode('utf-8'))
        expected_filters = {
            'field_date': [
                {'name': 'Equal to', 'operator': 'eq'},
                {'name': 'Greater than', 'operator': 'gt'},
                {'name': 'Smaller than', 'operator': 'lt'},
                {'name': 'Not Equal to', 'operator': 'neq'}
            ],
            'field_float': [
                {'name': 'Equal to', 'operator': 'eq'},
                {'name': 'Greater than', 'operator': 'gt'},
                {'name': 'Smaller than', 'operator': 'lt'},
                {'name': 'Not Equal to', 'operator': 'neq'}
            ],
            'field_integer': [
                {'name': 'Equal to', 'operator': 'eq'},
                {'name': 'Greater than', 'operator': 'gt'},
                {'name': 'Smaller than', 'operator': 'lt'},
                {'name': 'Not Equal to', 'operator': 'neq'}
            ],
            'field_string': [
                {'name': 'Starts with', 'operator': 'sw'},
                {'name': 'Ends with', 'operator': 'ew'},
                {'name': 'Contains', 'operator': 'ct'},
                {'name': 'Equal to', 'operator': 'eq'},
                {'name': 'Not Starts with', 'operator': 'nsw'},
                {'name': 'Not Ends with', 'operator': 'new'},
                {'name': 'Not Contains', 'operator': 'nct'},
                {'name': 'Not Equal to', 'operator': 'neq'}
            ]
        }
        eq_(data['filters'], expected_filters)

    def test_delete_item(self):
        """
            REST Api: Test delete item
        """
        client = self.app.test_client()
        pk = 2
        rv = client.delete('api/v1/model1api/{}'.format(pk))
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model1).get(pk)
        eq_(model, None)

    def test_delete_item_not_found(self):
        """
            REST Api: Test delete item not found
        """
        client = self.app.test_client()
        pk = 11
        rv = client.delete('api/v1/model1api/{}'.format(pk))
        eq_(rv.status_code, 404)

    def test_update_item(self):
        """
            REST Api: Test update item
        """
        client = self.app.test_client()
        pk = 3
        item = dict(
            field_string="test_Put",
            field_integer=0,
            field_float=0.0
        )
        rv = client.put('api/v1/model1api/{}'.format(pk), json=item)
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model1).get(pk)
        eq_(model.field_string, "test_Put")
        eq_(model.field_integer, 0)
        eq_(model.field_float, 0.0)

    def test_update_item_not_found(self):
        """
            REST Api: Test update item not found
        """
        client = self.app.test_client()
        pk = 11
        item = dict(
            field_string="test_Put",
            field_integer=0,
            field_float=0.0
        )
        rv = client.put('api/v1/model1api/{}'.format(pk), json=item)
        eq_(rv.status_code, 404)

    def test_update_val_size(self):
        """
            REST Api: Test update validate size
        """
        client = self.app.test_client()
        pk = 1
        field_string = 'a' * 51
        item = dict(
            field_string=field_string,
            field_integer=11,
            field_float=11.0
        )
        rv = client.put('api/v1/model1api/{}'.format(pk), json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_string'][0], 'Longer than maximum length 50.')

    def test_get_update_item_val_type(self):
        """
            REST Api: Test update validate type
        """
        client = self.app.test_client()
        pk = 1
        item = dict(
            field_string="test11",
            field_integer="test11",
            field_float=11.0
        )
        rv = client.put('api/v1/model1api/{}'.format(pk), json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_integer'][0], 'Not a valid integer.')

        item = dict(
            field_string=11,
            field_integer=11,
            field_float=11.0
        )
        rv = client.post('api/v1/model1api/', json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_string'][0], 'Not a valid string.')

    def test_create_item(self):
        """
            REST Api: Test create item
        """
        client = self.app.test_client()
        item = dict(
            field_string="test11",
            field_integer=11,
            field_float=11.0,
            field_date=None
        )
        rv = client.post('api/v1/model1api/', json=item)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(rv.status_code, 201)
        eq_(data['result'], item)
        model = self.db.session.query(Model1).filter_by(field_string='test11').first()
        eq_(model.field_string, "test11")
        eq_(model.field_integer, 11)
        eq_(model.field_float, 11.0)

    def test_create_item_val_size(self):
        """
            REST Api: Test create validate size
        """
        client = self.app.test_client()
        field_string = 'a' * 51
        item = dict(
            field_string=field_string,
            field_integer=11,
            field_float=11.0
        )
        rv = client.post('api/v1/model1api/', json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_string'][0], 'Longer than maximum length 50.')

    def test_get_create_item_val_type(self):
        """
            REST Api: Test create validate type
        """
        client = self.app.test_client()
        item = dict(
            field_string="test11",
            field_integer="test11",
            field_float=11.0
        )
        rv = client.post('api/v1/model1api/', json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_integer'][0], 'Not a valid integer.')

        item = dict(
            field_string=11,
            field_integer=11,
            field_float=11.0
        )
        rv = client.post('api/v1/model1api/', json=item)
        eq_(rv.status_code, 400)
        data = json.loads(rv.data.decode('utf-8'))
        eq_(data['message']['field_string'][0], 'Not a valid string.')

    def test_get_list_col_function(self):
        """
            REST Api: Test get list of objects with columns as functions
        """
        client = self.app.test_client()
        rv = client.get('api/v1/model1funcapi/')
        data = json.loads(rv.data.decode('utf-8'))
        # Tests count property
        eq_(data['count'], MODEL1_DATA_SIZE)
        # Tests data result default page size
        eq_(len(data['result']), self.model1api.page_size)
        for i in range(1, MODEL1_DATA_SIZE):
            item = data['result'][i - 1]
            eq_(item['full_concat'], "{}.{}.{}.{}".format(
                    "test" + str(i - 1),
                    i - 1,
                    float(i - 1),
                    None
                )
            )

