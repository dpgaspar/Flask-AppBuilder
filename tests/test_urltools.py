import os

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.tests.sqla.models import Model1
from flask_appbuilder.urltools import get_filter_args

from .base import FABTestCase


class FlaskTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_get_filter_args_allow_one(self):
        datamodel = SQLAInterface(Model1)
        with self.appbuilder.get_app.test_request_context(
            "/users/list?_flt_1_field_string=a"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == [["a"]]

    def test_get_filter_args_allow_multiple(self):
        datamodel = SQLAInterface(Model1)
        with self.appbuilder.get_app.test_request_context(
            "/users/list?_flt_1_field_string=a&_flt_1_field_integer=2"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values in ([["a"], ["2"]], [["2"], ["a"]])

    def test_get_filter_args_disallow(self):
        datamodel = SQLAInterface(Model1)
        with self.appbuilder.get_app.test_request_context(
            "/users/list?_flt_1_field_float=1.0"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == []

    def test_get_filter_args_disallow_off(self):
        datamodel = SQLAInterface(Model1)
        with self.appbuilder.get_app.test_request_context(
            "/users/list?_flt_1_field_float=1.0"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters, disallow_if_not_in_search=False)
            assert filters.values == [["1.0"]]

    def test_get_filter_args_invalid_index(self):
        datamodel = SQLAInterface(Model1)
        with self.appbuilder.get_app.test_request_context(
            "/users/list?_flt_a_field_string=a"
        ):
            filters = datamodel.get_filters(["field_string", "field_integer"])
            get_filter_args(filters)
            assert filters.values == []
