import os

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.urltools import get_filter_args
from tests.base import FABTestCase
from tests.sqla.models import Model1


class FlaskTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)

    def tearDown(self):
        self.ctx.pop()

    def test_get_filter_args_allow_one(self):
        datamodel = SQLAInterface(Model1)
        with self.app.test_request_context("/users/list?_flt_1_field_string=a"):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == [["a"]]

    def test_get_filter_args_allow_multiple(self):
        datamodel = SQLAInterface(Model1)
        with self.app.test_request_context(
            "/users/list?_flt_1_field_string=a&_flt_1_field_integer=2"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values in ([["a"], ["2"]], [["2"], ["a"]])

    def test_get_filter_args_disallow(self):
        datamodel = SQLAInterface(Model1)
        with self.app.test_request_context("/users/list?_flt_1_field_float=1.0"):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == []

    def test_get_filter_args_disallow_off(self):
        datamodel = SQLAInterface(Model1)
        with self.app.test_request_context("/users/list?_flt_1_field_float=1.0"):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters, disallow_if_not_in_search=False)
            assert filters.values == [["1.0"]]

    def test_get_filter_args_invalid_index(self):
        datamodel = SQLAInterface(Model1)
        with self.app.test_request_context("/users/list?_flt_a_field_string=a"):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == []
