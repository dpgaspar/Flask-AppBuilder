import datetime
import json
import logging
import os
import random
import string
import unittest

from flask import redirect, request, session
from flask_appbuilder import SQLA
from flask_appbuilder.charts.views import (
    ChartView,
    DirectByChartView,
    DirectChartView,
    GroupByChartView,
    TimeChartView,
)
from flask_appbuilder.models.generic import PSModel
from flask_appbuilder.models.generic import PSSession
from flask_appbuilder.models.generic.interface import GenericInterface
from flask_appbuilder.models.group import aggregate_avg, aggregate_count, aggregate_sum
from flask_appbuilder.models.sqla.filters import FilterEqual, FilterStartsWith
from flask_appbuilder.views import CompactCRUDMixin, MasterDetailView
import jinja2
from nose.tools import eq_, ok_

from .sqla.models import Model1, Model2, Model3, ModelWithEnums, TmpEnum


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


"""
    Constant english display string from framework
"""
DEFAULT_INDEX_STRING = "Welcome"
INVALID_LOGIN_STRING = "Invalid login"
ACCESS_IS_DENIED = "Access is Denied"
UNIQUE_VALIDATION_STRING = "Already exists"
NOTNULL_VALIDATION_STRING = "This field is required"
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "general"
REDIRECT_OBJ_ID = 1
USERNAME_READONLY = "readonly"
PASSWORD_READONLY = "readonly"

log = logging.getLogger(__name__)


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.models.sqla.interface import SQLAInterface
        from flask_appbuilder.views import ModelView

        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
        self.app.config["CSRF_ENABLED"] = False
        self.app.config["SECRET_KEY"] = "thisismyscretkey"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["FAB_ROLES"] = {
            "ReadOnly": [
                [".*", "can_list"],
                [".*", "can_show"]
            ]
        }

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        sess = PSSession()

        class PSView(ModelView):
            datamodel = GenericInterface(PSModel, sess)
            base_permissions = ["can_list", "can_show"]
            list_columns = ["UID", "C", "CMD", "TIME"]
            search_columns = ["UID", "C", "CMD"]

        class Model2View(ModelView):
            datamodel = SQLAInterface(Model2)
            list_columns = [
                "field_integer",
                "field_float",
                "field_string",
                "field_method",
                "group.field_string",
            ]
            edit_form_query_rel_fields = {
                "group": [["field_string", FilterEqual, "G2"]]
            }
            add_form_query_rel_fields = {"group": [["field_string", FilterEqual, "G1"]]}

        class Model22View(ModelView):
            datamodel = SQLAInterface(Model2)
            list_columns = [
                "field_integer",
                "field_float",
                "field_string",
                "field_method",
                "group.field_string",
            ]
            add_exclude_columns = ["excluded_string"]
            edit_exclude_columns = ["excluded_string"]
            show_exclude_columns = ["excluded_string"]

        class Model1View(ModelView):
            datamodel = SQLAInterface(Model1)
            related_views = [Model2View]
            list_columns = ["field_string", "field_file"]

        class Model3View(ModelView):
            datamodel = SQLAInterface(Model3)
            list_columns = ["pk1", "pk2", "field_string"]
            add_columns = ["pk1", "pk2", "field_string"]
            edit_columns = ["pk1", "pk2", "field_string"]

        class Model1CompactView(CompactCRUDMixin, ModelView):
            datamodel = SQLAInterface(Model1)

        class Model3CompactView(CompactCRUDMixin, ModelView):
            datamodel = SQLAInterface(Model3)

        class Model1ViewWithRedirects(ModelView):
            datamodel = SQLAInterface(Model1)
            obj_id = 1

            def post_add_redirect(self):
                return redirect(
                    "model1viewwithredirects/show/{0}".format(REDIRECT_OBJ_ID)
                )

            def post_edit_redirect(self):
                return redirect(
                    "model1viewwithredirects/show/{0}".format(REDIRECT_OBJ_ID)
                )

            def post_delete_redirect(self):
                return redirect(
                    "model1viewwithredirects/show/{0}".format(REDIRECT_OBJ_ID)
                )

        class Model1Filtered1View(ModelView):
            datamodel = SQLAInterface(Model1)
            base_filters = [["field_string", FilterStartsWith, "a"]]

        class Model1MasterView(MasterDetailView):
            datamodel = SQLAInterface(Model1)
            related_views = [Model2View]

        class Model1Filtered2View(ModelView):
            datamodel = SQLAInterface(Model1)
            base_filters = [["field_integer", FilterEqual, 0]]

        class Model2ChartView(ChartView):
            datamodel = SQLAInterface(Model2)
            chart_title = "Test Model1 Chart"
            group_by_columns = ["field_string"]

        class Model2GroupByChartView(GroupByChartView):
            datamodel = SQLAInterface(Model2)
            chart_title = "Test Model1 Chart"

            definitions = [
                {
                    "group": "field_string",
                    "series": [
                        (
                            aggregate_sum,
                            "field_integer",
                            aggregate_avg,
                            "field_integer",
                            aggregate_count,
                            "field_integer",
                        )
                    ],
                }
            ]

        class Model2DirectByChartView(DirectByChartView):
            datamodel = SQLAInterface(Model2)
            chart_title = "Test Model1 Chart"
            list_title = ""

            definitions = [
                {"group": "field_string", "series": ["field_integer", "field_float"]}
            ]

        class Model2TimeChartView(TimeChartView):
            datamodel = SQLAInterface(Model2)
            chart_title = "Test Model1 Chart"
            group_by_columns = ["field_date"]

        class Model2DirectChartView(DirectChartView):
            datamodel = SQLAInterface(Model2)
            chart_title = "Test Model1 Chart"
            direct_columns = {"stat1": ("group", "field_integer")}

        class Model1MasterChartView(MasterDetailView):
            datamodel = SQLAInterface(Model1)
            related_views = [Model2DirectByChartView]

        class Model1FormattedView(ModelView):
            datamodel = SQLAInterface(Model1)
            list_columns = ["field_string"]
            show_columns = ["field_string"]
            formatters_columns = {"field_string": lambda x: "FORMATTED_STRING"}

        class ModelWithEnumsView(ModelView):
            datamodel = SQLAInterface(ModelWithEnums)

        class Model1PermOverride(ModelView):
            datamodel = SQLAInterface(Model1)
            class_permission_name = 'view'
            method_permission_name = {
                "list": "access",
                "show": "access",
                "edit": "access",
                "add": "access",
                "delete": "access",
                "download": "access",
                "api_readvalues": "access",
                "api_column_edit": "access",
                "api_column_add": "access",
                "api_delete": "access",
                "api_update": "access",
                "api_create": "access",
                "api_get": "access",
                "api_read": "access",
                "api": "access"
            }

        self.model1permoverride = Model1PermOverride
        self.appbuilder.add_view_no_menu(Model1PermOverride)

        self.appbuilder.add_view(Model1View, "Model1", category="Model1")
        self.appbuilder.add_view(
            Model1ViewWithRedirects, "Model1ViewWithRedirects", category="Model1"
        )
        self.appbuilder.add_view(Model1CompactView, "Model1Compact", category="Model1")
        self.appbuilder.add_view(Model1MasterView, "Model1Master", category="Model1")
        self.appbuilder.add_view(
            Model1MasterChartView, "Model1MasterChart", category="Model1"
        )
        self.appbuilder.add_view(
            Model1Filtered1View, "Model1Filtered1", category="Model1"
        )
        self.appbuilder.add_view(
            Model1Filtered2View, "Model1Filtered2", category="Model1"
        )
        self.appbuilder.add_view(
            Model1FormattedView, "Model1FormattedView", category="Model1FormattedView"
        )

        self.appbuilder.add_view(Model2View, "Model2")
        self.appbuilder.add_view(Model22View, "Model22")
        self.appbuilder.add_view(Model2View, "Model2 Add", href="/model2view/add")
        self.appbuilder.add_view(Model2ChartView, "Model2 Chart")
        self.appbuilder.add_view(Model2GroupByChartView, "Model2 Group By Chart")
        self.appbuilder.add_view(Model2DirectByChartView, "Model2 Direct By Chart")
        self.appbuilder.add_view(Model2TimeChartView, "Model2 Time Chart")
        self.appbuilder.add_view(Model2DirectChartView, "Model2 Direct Chart")

        self.appbuilder.add_view(Model3View, "Model3")
        self.appbuilder.add_view(Model3CompactView, "Model3Compact")

        self.appbuilder.add_view(ModelWithEnumsView, "ModelWithEnums")

        self.appbuilder.add_view(PSView, "Generic DS PS View", category="PSView")
        role_admin = self.appbuilder.sm.find_role("Admin")
        self.appbuilder.sm.add_user(
            "admin", "admin", "user", "admin@fab.org", role_admin, "general"
        )
        role_read_only = self.appbuilder.sm.find_role("ReadOnly")
        self.appbuilder.sm.add_user(
            USERNAME_READONLY,
            "readonly",
            "readonly",
            "readonly@fab.org",
            role_read_only,
            PASSWORD_READONLY
        )

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("TEAR DOWN")

    """ ---------------------------------
            TEST HELPER FUNCTIONS
        ---------------------------------
    """

    def login(self, client, username, password):
        # Login with default admin
        return client.post(
            "/login/",
            data=dict(username=username, password=password),
            follow_redirects=True,
        )

    def logout(self, client):
        return client.get("/logout/")

    def insert_data(self):
        for x, i in zip(string.ascii_letters[:23], range(23)):
            model = Model1(field_string="%stest" % (x), field_integer=i)
            self.db.session.add(model)
            self.db.session.commit()

    def insert_data2(self):
        models1 = [
            Model1(field_string="G1"),
            Model1(field_string="G2"),
            Model1(field_string="G3"),
        ]
        for model1 in models1:
            try:
                self.db.session.add(model1)
                self.db.session.commit()
                for x, i in zip(string.ascii_letters[:10], range(10)):
                    model = Model2(
                        field_string="%stest" % (x),
                        field_integer=random.randint(1, 10),
                        field_float=random.uniform(0.0, 1.0),
                        group=model1,
                    )
                    year = random.choice(range(1900, 2012))
                    month = random.choice(range(1, 12))
                    day = random.choice(range(1, 28))
                    model.field_date = datetime.datetime(year, month, day)

                    self.db.session.add(model)
                    self.db.session.commit()
            except Exception as e:
                print("ERROR {0}".format(str(e)))
                self.db.session.rollback()

    def insert_data3(self):
        model3 = Model3(pk1=3, pk2=datetime.datetime(2017, 3, 3), field_string="foo")
        try:
            self.db.session.add(model3)
            self.db.session.commit()
        except Exception as e:
            print("Error {0}".format(str(e)))
            self.db.session.rollback()

    def test_fab_views(self):
        """
            Test views creation and registration
        """
        eq_(len(self.appbuilder.baseviews), 35)

    def test_back(self):
        """
            Test Back functionality
        """
        with self.app.test_client() as c:
            self.login(c, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
            c.get("/model1view/list/?_flt_0_field_string=f")
            c.get("/model2view/list/")
            c.get("/back", follow_redirects=True)
            assert request.args["_flt_0_field_string"] == u"f"
            assert "/model1view/list/" == request.path

    def test_model_creation(self):
        """
            Test Model creation
        """
        from sqlalchemy.engine.reflection import Inspector

        engine = self.db.session.get_bind(mapper=None, clause=None)
        inspector = Inspector.from_engine(engine)
        # Check if tables exist
        ok_("model1" in inspector.get_table_names())
        ok_("model2" in inspector.get_table_names())
        ok_("model3" in inspector.get_table_names())
        ok_("model_with_enums" in inspector.get_table_names())

    def test_index(self):
        """
            Test initial access and index message
        """
        client = self.app.test_client()

        # Check for Welcome Message
        rv = client.get("/")
        data = rv.data.decode("utf-8")
        ok_(DEFAULT_INDEX_STRING in data)

    def test_sec_login(self):
        """
            Test Security Login, Logout, invalid login, invalid access
        """
        client = self.app.test_client()

        # Try to List and Redirect to Login
        rv = client.get("/model1view/list/")
        eq_(rv.status_code, 302)
        rv = client.get("/model2view/list/")
        eq_(rv.status_code, 302)

        # Login and list with admin
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get("/model1view/list/")
        eq_(rv.status_code, 200)
        rv = client.get("/model2view/list/")
        eq_(rv.status_code, 200)

        # Logout and and try to list
        self.logout(client)
        rv = client.get("/model1view/list/")
        eq_(rv.status_code, 302)
        rv = client.get("/model2view/list/")
        eq_(rv.status_code, 302)

        # Invalid Login
        rv = self.login(client, DEFAULT_ADMIN_USER, "password")
        data = rv.data.decode("utf-8")
        ok_(INVALID_LOGIN_STRING in data)

    def test_auth_builtin_roles(self):
        """
            Test Security builtin roles readonly
        """
        self.insert_data()
        client = self.app.test_client()
        self.login(client, USERNAME_READONLY, PASSWORD_READONLY)
        # Test unauthorized GET
        rv = client.get("/model1view/list/")
        eq_(rv.status_code, 200)
        # Test unauthorized EDIT
        rv = client.get("/model1view/show/1")
        eq_(rv.status_code, 200)
        rv = client.get("/model1view/edit/1")
        eq_(rv.status_code, 302)
        # Test unauthorized DELETE
        rv = client.get("/model1view/delete/1")
        eq_(rv.status_code, 302)

    def test_sec_reset_password(self):
        """
            Test Security reset password
        """
        client = self.app.test_client()

        # Try Reset My password
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        ok_(ACCESS_IS_DENIED in data)

        # Reset My password
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        ok_("Reset Password Form" in data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="password", conf_password="password"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        self.logout(client)
        self.login(client, DEFAULT_ADMIN_USER, "password")
        rv = client.post(
            "/resetmypassword/form",
            data=dict(
                password=DEFAULT_ADMIN_PASSWORD, conf_password=DEFAULT_ADMIN_PASSWORD
            ),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

        # Reset Password Admin
        rv = client.get("/users/action/resetpasswords/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        ok_("Reset Password Form" in data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(
                password=DEFAULT_ADMIN_PASSWORD, conf_password=DEFAULT_ADMIN_PASSWORD
            ),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

    def test_generic_interface(self):
        """
            Test Generic Interface for generic-alter datasource
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get("/psview/list")
        rv.data.decode("utf-8")

    def test_model_crud(self):
        """
            Test Model add, delete, edit
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post(
            "/model1view/add",
            data=dict(
                field_string="test1",
                field_integer="1",
                field_float="0.12",
                field_date="2014-01-01",
            ),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

        model = self.db.session.query(Model1).first()
        eq_(model.field_string, u"test1")
        eq_(model.field_integer, 1)

        rv = client.post(
            "/model1view/edit/1",
            data=dict(field_string="test2", field_integer="2"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

        model = self.db.session.query(Model1).first()
        eq_(model.field_string, u"test2")
        eq_(model.field_integer, 2)

        rv = client.get("/model1view/delete/1", follow_redirects=True)
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model1).first()
        eq_(model, None)

    def test_model_crud_composite_pk(self):
        """
            Test Generic Interface for generic-alter datasource where model has composite
            primary keys
        """
        try:
            from urllib import quote
        except Exception:
            from urllib.parse import quote

        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post(
            "/model3view/add",
            data=dict(pk1="1", pk2="2017-01-01 00:00:00", field_string="foo"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        eq_(model.pk1, 1)
        eq_(model.pk2, datetime.datetime(2017, 1, 1))
        eq_(model.field_string, u"foo")

        pk = '[1, {"_type": "datetime", "value": "2017-01-01T00:00:00.000000"}]'
        rv = client.get("/model3view/show/" + quote(pk), follow_redirects=True)
        eq_(rv.status_code, 200)

        rv = client.post(
            "/model3view/edit/" + quote(pk),
            data=dict(pk1="2", pk2="2017-02-02 00:00:00", field_string="bar"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        eq_(model.pk1, 2)
        eq_(model.pk2, datetime.datetime(2017, 2, 2))
        eq_(model.field_string, u"bar")

        pk = '[2, {"_type": "datetime", "value": "2017-02-02T00:00:00.000000"}]'
        rv = client.get("/model3view/delete/" + quote(pk), follow_redirects=True)
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        eq_(model, None)

    def test_model_crud_with_enum(self):
        """
            Test Model add, delete, edit for Model with Enum Columns
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        data = {"enum1": u"e1", "enum2": "e1"}
        rv = client.post("/modelwithenumsview/add", data=data, follow_redirects=True)
        eq_(rv.status_code, 200)

        model = self.db.session.query(ModelWithEnums).first()
        eq_(model.enum1, u"e1")
        eq_(model.enum2, TmpEnum.e1)

        data = {"enum1": u"e2", "enum2": "e2"}
        rv = client.post("/modelwithenumsview/edit/1", data=data, follow_redirects=True)
        eq_(rv.status_code, 200)

        model = self.db.session.query(ModelWithEnums).first()
        eq_(model.enum1, u"e2")
        eq_(model.enum2, TmpEnum.e2)

        rv = client.get("/modelwithenumsview/delete/1", follow_redirects=True)
        eq_(rv.status_code, 200)
        model = self.db.session.query(ModelWithEnums).first()
        eq_(model, None)

    def test_formatted_cols(self):
        """
            Test ModelView's formatters_columns
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data()
        rv = client.get("/model1formattedview/list/")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("FORMATTED_STRING" in data)
        rv = client.get("/model1formattedview/show/1")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("FORMATTED_STRING" in data)

    def test_model_redirects(self):
        """
            Test Model redirects after add, delete, edit
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        model1 = Model1(field_string="Test Redirects")
        self.db.session.add(model1)
        model1.id = REDIRECT_OBJ_ID
        self.db.session.flush()

        rv = client.post(
            "/model1viewwithredirects/add",
            data=dict(
                field_string="test_redirect",
                field_integer="1",
                field_float="0.12",
                field_date="2014-01-01",
            ),
            follow_redirects=True,
        )

        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("Test Redirects" in data)

        model_id = (
            self.db.session.query(Model1)
            .filter_by(field_string="test_redirect")
            .first()
            .id
        )
        rv = client.post(
            "/model1viewwithredirects/edit/{0}".format(model_id),
            data=dict(field_string="test_redirect_2", field_integer="2"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        ok_("Test Redirects" in data)

        rv = client.get(
            "/model1viewwithredirects/delete/{0}".format(model_id),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        ok_("Test Redirects" in data)

    def test_excluded_cols(self):
        """
            Test add_exclude_columns, edit_exclude_columns, show_exclude_columns
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get("/model22view/add")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("field_string" in data)
        ok_("field_integer" in data)
        ok_("field_float" in data)
        ok_("field_date" in data)
        ok_("excluded_string" not in data)
        self.insert_data2()
        rv = client.get("/model22view/edit/1")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("field_string" in data)
        ok_("field_integer" in data)
        ok_("field_float" in data)
        ok_("field_date" in data)
        ok_("excluded_string" not in data)
        rv = client.get("/model22view/show/1")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("Field String" in data)
        ok_("Field Integer" in data)
        ok_("Field Float" in data)
        ok_("Field Date" in data)
        ok_("Excluded String" not in data)

    def test_query_rel_fields(self):
        """
            Test add and edit form related fields filter
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()

        # Base filter string starts with
        rv = client.get("/model2view/add")
        data = rv.data.decode("utf-8")
        ok_("G1" in data)
        ok_("G2" not in data)

        # Base filter string starts with
        rv = client.get("/model2view/edit/1")
        data = rv.data.decode("utf-8")
        ok_("G2" in data)
        ok_("G1" not in data)

    def test_model_list_order(self):
        """
            Test Model order on lists
        """
        self.insert_data()

        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post(
            "/model1view/list?_oc_Model1View=field_string&_od_Model1View=asc",
            follow_redirects=True,
        )
        # TODO: Fix this 405 error
        # eq_(rv.status_code, 200)
        rv.data.decode("utf-8")
        # TODO
        # VALIDATE LIST IS ORDERED
        rv = client.post(
            "/model1view/list?_oc_Model1View=field_string&_od_Model1View=desc",
            follow_redirects=True,
        )
        # TODO: Fix this 405 error
        # eq_(rv.status_code, 200)
        rv.data.decode("utf-8")
        # TODO
        # VALIDATE LIST IS ORDERED

    def test_model_add_validation(self):
        """
            Test Model add validations
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post(
            "/model1view/add",
            data=dict(field_string="test1", field_integer="1"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

        rv = client.post(
            "/model1view/add",
            data=dict(field_string="test1", field_integer="2"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_(UNIQUE_VALIDATION_STRING in data)

        model = self.db.session.query(Model1).all()
        eq_(len(model), 1)

        rv = client.post(
            "/model1view/add",
            data=dict(field_string="", field_integer="1"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_(NOTNULL_VALIDATION_STRING in data)

        model = self.db.session.query(Model1).all()
        eq_(len(model), 1)

    def test_model_edit_validation(self):
        """
            Test Model edit validations
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        client.post(
            "/model1view/add",
            data=dict(field_string="test1", field_integer="1"),
            follow_redirects=True,
        )
        client.post(
            "/model1view/add",
            data=dict(field_string="test2", field_integer="1"),
            follow_redirects=True,
        )
        rv = client.post(
            "/model1view/edit/1",
            data=dict(field_string="test2", field_integer="2"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_(UNIQUE_VALIDATION_STRING in data)

        rv = client.post(
            "/model1view/edit/1",
            data=dict(field_string="", field_integer="2"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_(NOTNULL_VALIDATION_STRING in data)

    def test_model_base_filter(self):
        """
            Test Model base filtered views
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data()
        models = self.db.session.query(Model1).all()
        eq_(len(models), 23)

        # Base filter string starts with
        rv = client.get("/model1filtered1view/list/")
        data = rv.data.decode("utf-8")
        ok_("atest" in data)
        ok_("btest" not in data)

        # Base filter integer equals
        rv = client.get("/model1filtered2view/list/")
        data = rv.data.decode("utf-8")
        ok_("atest" in data)
        ok_("btest" not in data)

    def test_model_list_method_field(self):
        """
            Tests a model's field has a method
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        rv = client.get("/model2view/list/")
        eq_(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        ok_("field_method_value" in data)

    def test_compactCRUDMixin(self):
        """
            Test CompactCRUD Mixin view
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        rv = client.get("/model1compactview/list/")
        eq_(rv.status_code, 200)

        # test with composite pk
        try:
            from urllib import quote
        except Exception:
            from urllib.parse import quote

        self.insert_data3()
        pk = '[3, {"_type": "datetime", "value": "2017-03-03T00:00:00"}]'
        rv = client.post(
            "/model3compactview/edit/" + quote(pk),
            data=dict(field_string="bar"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        eq_(model.field_string, u"bar")

        rv = client.get("/model3compactview/delete/" + quote(pk), follow_redirects=True)
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        eq_(model, None)

    def test_edit_add_form_action_prefix_for_compactCRUDMixin(self):
        """
            Test form_action in add, form_action in edit (CompactCRUDMixin)
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        # Make sure we have something to edit.
        self.insert_data()

        prefix = "/some-prefix"
        base_url = "http://localhost" + prefix
        session_form_action_key = "Model1CompactView__session_form_action"

        with client as c:
            expected_form_action = prefix + "/model1compactview/add/?"

            c.get("/model1compactview/add/", base_url=base_url)
            ok_(session[session_form_action_key] == expected_form_action)

            expected_form_action = prefix + "/model1compactview/edit/1?"
            c.get("/model1compactview/edit/1", base_url=base_url)

            ok_(session[session_form_action_key] == expected_form_action)

    def test_charts_view(self):
        """
            Test Various Chart views
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        log.info("CHART TEST")
        rv = client.get("/model2chartview/chart/")
        eq_(rv.status_code, 200)
        rv = client.get("/model2groupbychartview/chart/")
        eq_(rv.status_code, 200)
        rv = client.get("/model2directbychartview/chart/")
        eq_(rv.status_code, 200)
        rv = client.get("/model2timechartview/chart/")
        eq_(rv.status_code, 200)
        # TODO: fix this
        # rv = client.get('/model2directchartview/chart/')
        # eq_(rv.status_code, 200)

    def test_master_detail_view(self):
        """
            Test Master detail view
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        rv = client.get("/model1masterview/list/")
        eq_(rv.status_code, 200)
        rv = client.get("/model1masterview/list/1")
        eq_(rv.status_code, 200)

        rv = client.get("/model1masterchartview/list/")
        eq_(rv.status_code, 200)
        rv = client.get("/model1masterchartview/list/1")
        eq_(rv.status_code, 200)

    def test_api_read(self):
        """
        Testing the api/read endpoint
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data()
        rv = client.get("/model1formattedview/api/read")
        eq_(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        assert "result" in data
        assert "pks" in data
        assert len(data.get("result")) > 10

    def test_api_create(self):
        """
        Testing the api/create endpoint
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.post(
            "/model1view/api/create",
            data=dict(field_string="zzz"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        objs = self.db.session.query(Model1).all()
        eq_(len(objs), 1)

    def test_api_update(self):
        """
        Validate that the api update endpoint updates [only] the fields in
        POST data
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data()
        item = self.db.session.query(Model1).filter_by(id=1).one()
        field_integer_before = item.field_integer
        rv = client.put(
            "/model1view/api/update/1",
            data=dict(field_string="zzz"),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)
        item = self.db.session.query(Model1).filter_by(id=1).one()
        eq_(item.field_string, "zzz")
        eq_(item.field_integer, field_integer_before)

    def test_permission_override(self):
        """
            MVC: Test permission name override
        """
        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_access",
            "view"
        )
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )

        client = self.app.test_client()

        self.login(client, "test", "test")
        rv = client.get("/model1permoverride/list/")
        eq_(rv.status_code, 200)
        rv = client.post(
            "/model1permoverride/add",
            data=dict(
                field_string="test1",
                field_integer="1",
                field_float="0.12",
                field_date="2014-01-01",
            ),
            follow_redirects=True,
        )
        eq_(rv.status_code, 200)

        model = self.db.session.query(Model1).first()
        eq_(model.field_string, u"test1")
        eq_(model.field_integer, 1)

    def test_permission_converge_compress(self):
        """
            MVC: Test permission name converge compress
        """
        from flask_appbuilder import ModelView
        from flask_appbuilder.models.sqla.interface import SQLAInterface

        class Model1PermConverge(ModelView):
            datamodel = SQLAInterface(Model1)
            class_permission_name = 'view2'
            previous_class_permission_name = 'Model1View'
            method_permission_name = {
                "list": "access",
                "show": "access",
                "edit": "access",
                "add": "access",
                "delete": "access",
                "download": "access",
                "api_readvalues": "access",
                "api_column_edit": "access",
                "api_column_add": "access",
                "api_delete": "access",
                "api_update": "access",
                "api_create": "access",
                "api_get": "access",
                "api_read": "access",
                "api": "access"
            }

        self.appbuilder.add_view_no_menu(Model1PermConverge)
        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_list",
            "Model1View"
        )
        self.appbuilder.sm.add_permission_role(role, pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_add",
            "Model1View"
        )
        self.appbuilder.sm.add_permission_role(role, pvm)
        role = self.appbuilder.sm.find_role("Test")
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )
        # Remove previous class, Hack to test code change
        for i, baseview in enumerate(self.appbuilder.baseviews):
            if baseview.__class__.__name__ == "Model1View":
                break
        self.appbuilder.baseviews.pop(i)
        for i, baseview in enumerate(self.appbuilder.baseviews):
            if baseview.__class__.__name__ == "Model1PermOverride":
                break
        self.appbuilder.baseviews.pop(i)

        target_state_transitions = {
            'add': {
                ('Model1View', 'can_edit'): {('view2', 'can_access')},
                ('Model1View', 'can_add'): {('view2', 'can_access')},
                ('Model1View', 'can_list'): {('view2', 'can_access')},
                ('Model1View', 'can_download'): {('view2', 'can_access')},
                ('Model1View', 'can_show'): {('view2', 'can_access')},
                ('Model1View', 'can_delete'): {('view2', 'can_access')}
            },
            'del_role_pvm': {
                ('Model1View', 'can_show'),
                ('Model1View', 'can_add'),
                ('Model1View', 'can_download'),
                ('Model1View', 'can_list'),
                ('Model1View', 'can_edit'),
                ('Model1View', 'can_delete')
            },
            'del_views': {
                'Model1View'
            },
            'del_perms': set()
        }
        state_transitions = self.appbuilder.security_converge()
        eq_(state_transitions, target_state_transitions)
        role = self.appbuilder.sm.find_role("Test")
        eq_(len(role.permissions), 1)
