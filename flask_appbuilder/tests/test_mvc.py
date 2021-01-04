import datetime
import json
import logging
from typing import Set

from flask import Flask, redirect, request, session
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.actions import action
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
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import CompactCRUDMixin, MasterDetailView, ModelView
from flask_wtf import CSRFProtect
import jinja2

from .base import FABTestCase
from .const import (
    MODEL1_DATA_SIZE,
    PASSWORD_ADMIN,
    PASSWORD_READONLY,
    USERNAME_ADMIN,
    USERNAME_READONLY,
)
from .sqla.models import (
    insert_model1,
    insert_model2,
    insert_model3,
    insert_model_with_enums,
    Model1,
    Model2,
    Model3,
    ModelWithEnums,
    TmpEnum,
)


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

log = logging.getLogger(__name__)


class MVCBabelTestCase(FABTestCase):
    def test_babel_empty_languages(self):
        """
            MVC: Test babel empty languages
        """
        app = Flask(__name__)
        app.config.from_object("flask_appbuilder.tests.config_api")
        app.config["LANGUAGES"] = {}
        db = SQLA(app)
        AppBuilder(app, db.session)

        client = app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/users/list/")
        self.assertEqual(rv.status_code, 200)

        data = rv.data.decode("utf-8")
        self.assertNotIn('class="f16', data)

    def test_babel_languages(self):
        """
            MVC: Test babel languages
        """
        app = Flask(__name__)
        app.config.from_object("flask_appbuilder.tests.config_api")
        app.config["LANGUAGES"] = {
            "en": {"flag": "gb", "name": "English"},
            "pt": {"flag": "pt", "name": "Portuguese"},
        }
        db = SQLA(app)
        AppBuilder(app, db.session)

        client = app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/users/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn('href="/lang/pt"', data)

        # Test babel language switch endpoint
        rv = client.get("/lang/pt")
        self.assertEqual(rv.status_code, 302)


class BaseMVCTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        logging.basicConfig(level=logging.ERROR)

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    @property
    def registered_endpoints(self) -> Set:
        return {item.endpoint for item in self.app.url_map.iter_rules()}

    def get_registered_view_endpoints(self, view_name) -> Set:
        return {
            item.endpoint
            for item in self.app.url_map.iter_rules()
            if item.endpoint.split(".")[0] == view_name
        }


class MVCCSRFTestCase(BaseMVCTestCase):
    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.csrf = CSRFProtect(self.app)
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        class Model2View(ModelView):
            datamodel = SQLAInterface(Model1)

        self.appbuilder.add_view(Model2View, "Model2", category="Model2")

    def test_a_csrf_delete_not_allowed(self):
        """
            MVC: Test GET delete with CSRF is not allowed
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model.id
        rv = client.get(f"/model2view/delete/{pk}")

        self.assertEqual(rv.status_code, 302)
        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        self.assertIsNotNone(model)

    def test_a_csrf_delete_protected(self):
        """
            MVC: Test POST delete with CSRF
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model.id
        rv = client.post(f"/model2view/delete/{pk}")
        # Missing CSRF token
        self.assertEqual(rv.status_code, 400)


class MVCSwitchRouteMethodsTestCase(BaseMVCTestCase):
    """
    Specific to test ModelView's:
        - include_route_methods
        - exclude_route_methods
        - disable_api_route_methods
    """

    def setUp(self):
        super().setUp()

        class Model2IncludeView(ModelView):
            datamodel = SQLAInterface(Model2)
            include_route_methods = {"list", "show"}

        self.appbuilder.add_view(Model2IncludeView, "Model2IncludeView")

        class Model2ExcludeView(ModelView):
            datamodel = SQLAInterface(Model2)
            exclude_route_methods: Set = {
                "api",
                "api_read",
                "api_get",
                "api_create",
                "api_update",
                "api_delete",
                "api_column_add",
                "api_column_edit",
                "api_readvalues",
            }

        self.appbuilder.add_view(Model2ExcludeView, "Model2ExcludeView")

        class Model2IncludeExcludeView(ModelView):
            datamodel = SQLAInterface(Model2)
            include_route_methods: Set = {
                "api",
                "api_read",
                "api_get",
                "api_create",
                "api_update",
                "api_delete",
                "api_column_add",
                "api_column_edit",
                "api_readvalues",
            }
            exclude_route_methods: Set = {
                "api_create",
                "api_update",
                "api_delete",
                "api_column_add",
                "api_column_edit",
                "api_readvalues",
            }

        self.appbuilder.add_view_no_menu(
            Model2IncludeExcludeView, "Model2IncludeExcludeView"
        )

        class Model2DisableMVCApiView(ModelView):
            datamodel = SQLAInterface(Model2)
            disable_api_route_methods = True

        self.appbuilder.add_view(Model2DisableMVCApiView, "Model2DisableMVCApiView")

    def test_include_route_methods(self):
        """
            MVC: Include route methods
        """
        expected_endpoints = {"Model2IncludeView.list", "Model2IncludeView.show"}
        self.assertEqual(
            expected_endpoints, self.get_registered_view_endpoints("Model2IncludeView")
        )
        # Check that permissions do not exist
        unexpected_permissions = [
            ("can_add", "Model2IncludeView"),
            ("can_edit", "Model2IncludeView"),
            ("can_delete", "Model2IncludeView"),
            ("can_download", "Model2IncludeView"),
        ]
        for unexpected_permission in unexpected_permissions:
            pvm = self.appbuilder.sm.find_permission_view_menu(*unexpected_permission)
            self.assertIsNone(pvm)
        # Login and list with admin, check that mutation links are not rendered
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model2includeview/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertNotIn("/model2includeview/add", data)
        self.assertNotIn("/model2includeview/edit", data)
        self.assertNotIn("/model2includeview/delete", data)

    def test_exclude_route_methods(self):
        """
            MVC: Exclude route methods
        """
        expected_endpoints: Set = {
            "Model2ExcludeView.list",
            "Model2ExcludeView.show",
            "Model2ExcludeView.edit",
            "Model2ExcludeView.download",
            "Model2ExcludeView.action",
            "Model2ExcludeView.delete",
            "Model2ExcludeView.add",
            "Model2ExcludeView.action_post",
        }
        self.assertEqual(
            expected_endpoints, self.get_registered_view_endpoints("Model2ExcludeView")
        )

    def test_include_exclude_route_methods(self):
        """
            MVC: Include and Exclude route methods
        """

        expected_endpoints: Set = {
            "Model2IncludeExcludeView.api",
            "Model2IncludeExcludeView.api_read",
            "Model2IncludeExcludeView.api_get",
        }
        self.assertEqual(
            expected_endpoints,
            self.get_registered_view_endpoints("Model2IncludeExcludeView"),
        )
        # Check that permissions do not exist
        unexpected_permissions = [
            ("can_add", "Model2IncludeExcludeView"),
            ("can_edit", "Model2IncludeExcludeView"),
            ("can_delete", "Model2IncludeExcludeView"),
            ("can_download", "Model2IncludeExcludeView"),
        ]
        for unexpected_permission in unexpected_permissions:
            pvm = self.appbuilder.sm.find_permission_view_menu(*unexpected_permission)
            self.assertIsNone(pvm)

    def test_disable_mvc_api_methods(self):
        """
            MVC: Disable MVC API
        """
        expected_endpoints: Set = {
            "Model2DisableMVCApiView.list",
            "Model2DisableMVCApiView.show",
            "Model2DisableMVCApiView.add",
            "Model2DisableMVCApiView.edit",
            "Model2DisableMVCApiView.delete",
            "Model2DisableMVCApiView.action",
            "Model2DisableMVCApiView.download",
            "Model2DisableMVCApiView.action_post",
        }
        self.assertEqual(
            expected_endpoints,
            self.get_registered_view_endpoints("Model2DisableMVCApiView"),
        )


class MVCTestCase(BaseMVCTestCase):
    def setUp(self):
        super().setUp()
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
                "group": [["field_string", FilterEqual, "test1"]]
            }
            add_form_query_rel_fields = {
                "group": [["field_string", FilterEqual, "test0"]]
            }

            order_columns = ["field_string", "group.field_string"]

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
            list_columns = ["field_string", "field_integer"]

        class Model3View(ModelView):
            datamodel = SQLAInterface(Model3)
            list_columns = ["pk1", "pk2", "field_string"]
            add_columns = ["pk1", "pk2", "field_string"]
            edit_columns = ["pk1", "pk2", "field_string"]

            @action(
                "muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False
            )
            def muldelete(self, items):
                self.datamodel.delete_all(items)
                self.update_redirect()
                return redirect(self.get_redirect())

        class Model1CompactView(CompactCRUDMixin, ModelView):
            datamodel = SQLAInterface(Model1)

        class Model3CompactView(CompactCRUDMixin, ModelView):
            datamodel = SQLAInterface(Model3)

        class Model1ViewWithRedirects(ModelView):
            datamodel = SQLAInterface(Model1)

            def post_add_redirect(self):
                return redirect("/")

            def post_edit_redirect(self):
                return redirect("/")

            def post_delete_redirect(self):
                return redirect("/")

        class Model1Filtered1View(ModelView):
            datamodel = SQLAInterface(Model1)
            base_filters = [["field_string", FilterStartsWith, "test2"]]

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
            PASSWORD_READONLY,
        )

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("TEAR DOWN")

    def test_fab_views(self):
        """
            Test views creation and registration
        """
        self.assertEqual(len(self.appbuilder.baseviews), 36)

    def test_back(self):
        """
            Test Back functionality
        """
        with self.app.test_client() as c:
            self.browser_login(c, USERNAME_ADMIN, PASSWORD_ADMIN)
            c.get("/model1view/list/?_flt_0_field_string=f")
            c.get("/model2view/list/")
            c.get("/back", follow_redirects=True)
            assert request.args["_flt_0_field_string"] == "f"
            assert "/model1view/list/" == request.path

    def test_model_creation(self):
        """
            Test Model creation
        """
        from sqlalchemy.engine.reflection import Inspector

        engine = self.db.session.get_bind(mapper=None, clause=None)
        inspector = Inspector.from_engine(engine)
        # Check if tables exist
        self.assertIn("model1", inspector.get_table_names())
        self.assertIn("model2", inspector.get_table_names())
        self.assertIn("model3", inspector.get_table_names())
        self.assertIn("model_with_enums", inspector.get_table_names())

    def test_index(self):
        """
            Test initial access and index message
        """
        client = self.app.test_client()

        # Check for Welcome Message
        rv = client.get("/")
        data = rv.data.decode("utf-8")
        self.assertIn(DEFAULT_INDEX_STRING, data)

    def test_sec_login(self):
        """
            Test Security Login, Logout, invalid login, invalid access
        """
        client = self.app.test_client()

        # Try to List and Redirect to Login
        rv = client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 302)
        rv = client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 302)

        # Login and list with admin
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 200)
        rv = client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 200)

        # Logout and and try to list
        self.browser_logout(client)
        rv = client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 302)
        rv = client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 302)

        # Invalid Login
        rv = self.browser_login(client, USERNAME_ADMIN, "wrong_password")
        data = rv.data.decode("utf-8")
        self.assertIn(INVALID_LOGIN_STRING, data)

    def test_auth_builtin_roles(self):
        """
            Test Security builtin roles readonly
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_READONLY, PASSWORD_READONLY)
        # Test authorized GET
        rv = client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 200)
        # Test authorized SHOW
        rv = client.get("/model1view/show/1")
        self.assertEqual(rv.status_code, 200)
        # Test unauthorized EDIT
        rv = client.get("/model1view/edit/1")
        self.assertEqual(rv.status_code, 302)
        # Test unauthorized DELETE
        rv = client.get("/model1view/delete/1")
        self.assertEqual(rv.status_code, 302)

    def test_sec_reset_password(self):
        """
            Test Security reset password
        """
        client = self.app.test_client()

        # Try Reset My password
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        # Werkzeug update to 0.15.X sends this action to wrong redirect
        # Old test was:
        # data = rv.data.decode("utf-8")
        # ok_(ACCESS_IS_DENIED in data)
        self.assertEqual(rv.status_code, 404)

        # Reset My password
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Reset Password Form", data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="password", conf_password="password"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        self.browser_logout(client)
        self.browser_login(client, USERNAME_ADMIN, "password")
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password=PASSWORD_ADMIN, conf_password=PASSWORD_ADMIN),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

        # Reset Password Admin
        rv = client.get("/users/action/resetpasswords/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Reset Password Form", data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password=PASSWORD_ADMIN, conf_password=PASSWORD_ADMIN),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

    def test_generic_interface(self):
        """
            Test Generic Interface for generic-alter datasource
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/psview/list", follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

    def test_model_crud_add(self):
        """
            Test ModelView CRUD Add
        """
        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        field_string = f"test{MODEL1_DATA_SIZE+1}"
        rv = client.post(
            "/model1view/add",
            data=dict(
                field_string=field_string,
                field_integer=f"{MODEL1_DATA_SIZE}",
                field_float=f"{float(MODEL1_DATA_SIZE)}",
                field_date="2014-01-01",
            ),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

        model = (
            self.db.session.query(Model1)
            .filter_by(field_string=field_string)
            .one_or_none()
        )
        self.assertEqual(model.field_string, field_string)
        self.assertEqual(model.field_integer, MODEL1_DATA_SIZE)

        # Revert data changes
        self.appbuilder.get_session.delete(model)
        self.appbuilder.get_session.commit()

    def test_model_crud_edit(self):
        """
            Test ModelView CRUD Edit
        """
        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model.id
        rv = client.post(
            f"/model1view/edit/{pk}",
            data=dict(field_string="test_edit", field_integer="200"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

        model = self.db.session.query(Model1).filter_by(id=pk).one_or_none()
        self.assertEqual(model.field_string, "test_edit")
        self.assertEqual(model.field_integer, 200)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=pk - 1)

    def test_model_crud_delete(self):
        """
            Test Model CRUD delete
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model.id
        rv = client.get(f"/model2view/delete/{pk}", follow_redirects=True)

        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model2).get(pk)
        self.assertEqual(model, None)

        # Revert data changes
        insert_model2(self.appbuilder.get_session, i=0)

    def test_model_delete_integrity(self):
        """
            Test Model CRUD delete integrity validation
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test1")
            .one_or_none()
        )
        pk = model1.id
        rv = client.get(f"/model1view/delete/{pk}", follow_redirects=True)

        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model1).filter_by(id=pk).one_or_none()
        self.assertNotEqual(model, None)

    def test_model_crud_composite_pk(self):
        """
            MVC CRUD generic-alter datasource where model has composite
            primary keys
        """
        try:
            from urllib import quote
        except Exception:
            from urllib.parse import quote

        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.post(
            "/model3view/add",
            data=dict(pk1="1", pk2=datetime.datetime(2017, 1, 1), field_string="foo2"),
            follow_redirects=True,
        )

        self.assertEqual(rv.status_code, 200)
        model = (
            self.appbuilder.get_session.query(Model3).filter_by(pk1="1").one_or_none()
        )
        self.assertEqual(model.pk1, 1)
        self.assertEqual(model.pk2, datetime.datetime(2017, 1, 1))
        self.assertEqual(model.field_string, "foo2")

        pk = '[1, {"_type": "datetime", "value": "2017-01-01T00:00:00.000000"}]'
        rv = client.get(f"/model3view/show/{quote(pk)}", follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = client.post(
            "/model3view/edit/" + quote(pk),
            data=dict(pk1="2", pk2="2017-02-02 00:00:00", field_string="bar"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

        model = (
            self.appbuilder.get_session.query(Model3)
            .filter_by(pk1="2", pk2="2017-02-02 00:00:00")
            .one_or_none()
        )
        self.assertEqual(model.pk1, 2)
        self.assertEqual(model.pk2, datetime.datetime(2017, 2, 2))
        self.assertEqual(model.field_string, "bar")

        pk = '[2, {"_type": "datetime", "value": "2017-02-02T00:00:00.000000"}]'
        rv = client.get("/model3view/delete/" + quote(pk), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model3).filter_by(pk1=2).one_or_none()
        self.assertEqual(model, None)

        # Add it back, then delete via muldelete
        self.appbuilder.get_session.add(
            Model3(pk1=1, pk2=datetime.datetime(2017, 1, 1), field_string="baz")
        )
        self.appbuilder.get_session.commit()
        rv = client.post(
            "/model3view/action_post",
            data=dict(
                action="muldelete",
                rowid=[
                    json.dumps(
                        [
                            "1",
                            {
                                "_type": "datetime",
                                "value": "2017-01-01T00:00:00.000000",
                            },
                        ]
                    )
                ],
            ),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model3).filter_by(pk1=1).one_or_none()
        self.assertEqual(model, None)

    def test_model_crud_add_with_enum(self):
        """
            Test Model add for Model with Enum Columns
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        data = {"enum1": "e3", "enum2": "e3"}
        rv = client.post("/modelwithenumsview/add", data=data, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        model = (
            self.appbuilder.get_session.query(ModelWithEnums)
            .filter_by(enum1="e3")
            .one_or_none()
        )
        self.assertIsNotNone(model)
        self.assertEqual(model.enum2, TmpEnum.e3)

        # Revert data changes
        model = (
            self.appbuilder.get_session.query(ModelWithEnums)
            .filter_by(enum1="e3")
            .one_or_none()
        )
        self.appbuilder.get_session.delete(model)
        self.appbuilder.get_session.commit()

    def test_model_crud_edit_with_enum(self):
        """
            Test Model edit for Model with Enum Columns
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        data = {"enum1": "e3", "enum2": "e3"}
        pk = 1
        rv = client.post(
            f"/modelwithenumsview/edit/{pk}", data=data, follow_redirects=True
        )
        self.assertEqual(rv.status_code, 200)

        model = (
            self.appbuilder.get_session.query(ModelWithEnums)
            .filter_by(enum1="e3")
            .one_or_none()
        )
        self.assertIsNotNone(model)
        self.assertEqual(model.enum2, TmpEnum.e3)

        # Revert data changes
        insert_model_with_enums(self.appbuilder.get_session, i=pk - 1)

    def test_formatted_cols(self):
        """
            Test ModelView's formatters_columns
        """
        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model1formattedview/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("FORMATTED_STRING", data)
        rv = client.get("/model1formattedview/show/1")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("FORMATTED_STRING", data)

    def test_modelview_add_redirects(self):
        """
            Test ModelView redirects after add
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.post(
            "/model1viewwithredirects/add", data=dict(field_string="test_redirect")
        )

        self.assertEqual(rv.status_code, 302)
        self.assertEqual("http://localhost/", rv.headers["Location"])

        # Revert data changes
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test_redirect")
            .one_or_none()
        )
        self.appbuilder.get_session.delete(model1)
        self.appbuilder.get_session.commit()

    def test_modelview_edit_redirects(self):
        """
            Test ModelView redirects after edit
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model_id = (
            self.db.session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
            .id
        )
        rv = client.post(
            f"/model1viewwithredirects/edit/{model_id}",
            data=dict(field_string="test_redirect", field_integer="200"),
        )
        self.assertEqual(rv.status_code, 302)
        self.assertEqual("http://localhost/", rv.headers["Location"])

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=model_id - 1)

    def test_modelview_delete_redirects(self):
        """
            Test ModelView redirects after delete
        """
        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model_id = (
            self.db.session.query(Model1).filter_by(field_string="test0").first().id
        )
        rv = client.get(f"/model1viewwithredirects/delete/{model_id}")
        self.assertEqual(rv.status_code, 302)
        self.assertEqual("http://localhost/", rv.headers["Location"])
        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=model_id - 1)

    def test_add_excluded_cols(self):
        """
            Test add_exclude_columns
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model22view/add")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("field_string", data)
        self.assertIn("field_integer", data)
        self.assertIn("field_float", data)
        self.assertIn("field_date", data)
        self.assertNotIn("excluded_string", data)

    def test_edit_excluded_cols(self):
        """
            Test edit_exclude_columns
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        rv = client.get(f"/model22view/edit/{model.id}")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("field_string", data)
        self.assertIn("field_integer", data)
        self.assertIn("field_float", data)
        self.assertIn("field_date", data)
        self.assertNotIn("excluded_string", data)

    def test_show_excluded_cols(self):
        """
            Test show_exclude_columns
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        rv = client.get(f"/model22view/show/{model.id}")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("Field String", data)
        self.assertIn("Field Integer", data)
        self.assertIn("Field Float", data)
        self.assertIn("Field Date", data)
        self.assertNotIn("Excluded String", data)

    def test_query_rel_fields(self):
        """
            Test add and edit form related fields filter
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Base filter string starts with
        rv = client.get("/model2view/add")
        data = rv.data.decode("utf-8")
        self.assertIn("test0", data)
        self.assertNotIn(f"test1", data)

        model2 = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        # Base filter string starts with
        rv = client.get(f"/model2view/edit/{model2.id}")
        data = rv.data.decode("utf-8")
        self.assertIn(f"test1", data)

    def test_model_list_order(self):
        """
            Test Model order on lists
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.get(
            "/model1view/list?_oc_Model1View=field_string&_od_Model1View=asc",
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("test0", data)
        rv = client.get(
            "/model1view/list?_oc_Model1View=field_string&_od_Model1View=desc",
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn(f"test{MODEL1_DATA_SIZE-1}", data)

    def test_model_list_order_related(self):
        """
        Test Model order related field on lists
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.get(
            "/model2view/list?_oc_Model2View=group.field_string&_od_Model2View=asc",
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

    def test_model_add_unique_validation(self):
        """
        Test Model add unique field validation
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Test unique constraint
        rv = client.post(
            "/model1view/add",
            data=dict(field_string="test1", field_integer="2"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn(UNIQUE_VALIDATION_STRING, data)

        model = self.db.session.query(Model1).all()
        self.assertEqual(len(model), MODEL1_DATA_SIZE)

    def test_model_add_required_validation(self):
        """
            Test Model add required fields validation
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Test field required
        rv = client.post(
            "/model1view/add",
            data=dict(field_string="", field_integer="1"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn(NOTNULL_VALIDATION_STRING, data)

        model = self.db.session.query(Model1).all()
        self.assertEqual(len(model), MODEL1_DATA_SIZE)

    def test_model_edit_unique_validation(self):
        """
            Test Model edit unique validation
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.post(
            "/model1view/edit/1",
            data=dict(field_string="test2", field_integer="2"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn(UNIQUE_VALIDATION_STRING, data)

    def test_model_edit_required_validation(self):
        """
            Test Model edit required validation
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = client.post(
            "/model1view/edit/1",
            data=dict(field_string="", field_integer="2"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn(NOTNULL_VALIDATION_STRING, data)

    def test_model_base_filter(self):
        """
            Test Model base filtered views
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        models = self.db.session.query(Model1).all()
        self.assertEqual(len(models), MODEL1_DATA_SIZE)

        # Base filter string starts with
        rv = client.get("/model1filtered1view/list/")
        data = rv.data.decode("utf-8")
        self.assertIn("test2", data)
        self.assertNotIn("test0", data)

        # Base filter integer equals
        rv = client.get("/model1filtered2view/list/")
        data = rv.data.decode("utf-8")
        self.assertIn("test0", data)
        self.assertNotIn("test1", data)

    def test_model_list_method_field(self):
        """
            Tests a model's field has a method
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("_field_method", data)

    def test_compactCRUDMixin(self):
        """
            Test CompactCRUD Mixin view with composite keys
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model1compactview/list/")
        self.assertEqual(rv.status_code, 200)

        # test with composite pk
        try:
            from urllib import quote
        except Exception:
            from urllib.parse import quote

        pk = '[3, {"_type": "datetime", "value": "2017-03-03T00:00:00"}]'
        rv = client.post(
            "/model3compactview/edit/" + quote(pk),
            data=dict(field_string="bar"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        self.assertEqual(model.field_string, "bar")

        rv = client.get("/model3compactview/delete/" + quote(pk), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model3).first()
        self.assertEqual(model, None)

        # Revert data changes
        insert_model3(self.appbuilder.get_session)

    def test_edit_add_form_action_prefix_for_compactCRUDMixin(self):
        """
            Test form_action in add, form_action in edit (CompactCRUDMixin)
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Make sure we have something to edit.
        prefix = "/some-prefix"
        base_url = "http://localhost" + prefix
        session_form_action_key = "Model1CompactView__session_form_action"

        with client as c:
            expected_form_action = prefix + "/model1compactview/add/?"

            c.get("/model1compactview/add/", base_url=base_url)
            self.assertEqual(session[session_form_action_key], expected_form_action)

            expected_form_action = prefix + "/model1compactview/edit/1?"
            c.get("/model1compactview/edit/1", base_url=base_url)

            self.assertEqual(session[session_form_action_key], expected_form_action)

    def test_charts_view(self):
        """
            Test Various Chart views
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        # self.insert_data2()
        rv = client.get("/model2chartview/chart/")
        self.assertEqual(rv.status_code, 200)
        rv = client.get("/model2groupbychartview/chart/")
        self.assertEqual(rv.status_code, 200)
        rv = client.get("/model2directbychartview/chart/")
        self.assertEqual(rv.status_code, 200)
        # TODO: fix this
        rv = client.get("/model2timechartview/chart/")
        self.assertEqual(rv.status_code, 200)

    def test_master_detail_view(self):
        """
            Test Master detail view
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        # self.insert_data2()
        rv = client.get("/model1masterview/list/")
        self.assertEqual(rv.status_code, 200)
        rv = client.get("/model1masterview/list/1")
        self.assertEqual(rv.status_code, 200)

        rv = client.get("/model1masterchartview/list/")
        self.assertEqual(rv.status_code, 200)
        rv = client.get("/model1masterchartview/list/1")
        self.assertEqual(rv.status_code, 200)

    def test_api_read(self):
        """
        Testing the api/read endpoint
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/model1formattedview/api/read")
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertIn("result", data)
        self.assertIn("pks", data)
        assert len(data.get("result")) > 10

    def test_api_create(self):
        """
        Testing the api/create endpoint
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.post(
            "/model1view/api/create",
            data=dict(field_string="zzz"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        model1 = (
            self.db.session.query(Model1).filter_by(field_string="zzz").one_or_none()
        )
        self.assertIsNotNone(model1)

        # Revert data changes
        self.appbuilder.get_session.delete(model1)
        self.appbuilder.get_session.commit()

    def test_api_update(self):
        """
        Validate that the api update endpoint updates [only] the fields in
        POST data
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = self.db.session.query(Model1).filter_by(id=1).one()
        field_integer_before = item.field_integer
        rv = client.put(
            "/model1view/api/update/1",
            data=dict(field_string="zzz"),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        item = self.db.session.query(Model1).filter_by(id=1).one()
        self.assertEqual(item.field_string, "zzz")
        self.assertEqual(item.field_integer, field_integer_before)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=0)

    def test_class_method_permission_override(self):
        """
            MVC: Test class method permission name override
        """
        from flask_appbuilder import ModelView
        from flask_appbuilder.models.sqla.interface import SQLAInterface

        class Model1PermOverride(ModelView):
            datamodel = SQLAInterface(Model1)
            class_permission_name = "view"
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
                "api": "access",
            }

        self.model1permoverride = Model1PermOverride
        self.appbuilder.add_view_no_menu(Model1PermOverride)

        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_access", "view")
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )

        client = self.app.test_client()

        self.browser_login(client, "test", "test")
        rv = client.get("/model1permoverride/list/")
        self.assertEqual(rv.status_code, 200)
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
        self.assertEqual(rv.status_code, 200)

        model = (
            self.db.session.query(Model1).filter_by(field_string="test1").one_or_none()
        )
        self.assertEqual(model.field_string, "test1")
        self.assertEqual(model.field_integer, 1)

    def test_method_permission_override(self):
        """
            MVC: Test method permission name override
        """
        from flask_appbuilder import ModelView
        from flask_appbuilder.models.sqla.interface import SQLAInterface

        class Model1PermOverride(ModelView):
            datamodel = SQLAInterface(Model1)
            method_permission_name = {
                "list": "read",
                "show": "read",
                "edit": "write",
                "add": "write",
                "delete": "write",
                "download": "read",
                "api_readvalues": "read",
                "api_column_edit": "write",
                "api_column_add": "write",
                "api_delete": "write",
                "api_update": "write",
                "api_create": "write",
                "api_get": "read",
                "api_read": "read",
                "api": "read",
            }

        self.model1permoverride = Model1PermOverride
        self.appbuilder.add_view_no_menu(Model1PermOverride)

        role = self.appbuilder.sm.add_role("Test")
        pvm_read = self.appbuilder.sm.find_permission_view_menu(
            "can_read", "Model1PermOverride"
        )
        pvm_write = self.appbuilder.sm.find_permission_view_menu(
            "can_write", "Model1PermOverride"
        )
        self.appbuilder.sm.add_permission_role(role, pvm_read)
        self.appbuilder.sm.add_permission_role(role, pvm_write)

        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )

        client = self.app.test_client()
        self.browser_login(client, "test", "test")

        rv = client.post(
            "/model1permoverride/add",
            data=dict(
                field_string=f"test{MODEL1_DATA_SIZE+1}",
                field_integer="1",
                field_float="0.12",
                field_date="2014-01-01",
            ),
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string=f"test{MODEL1_DATA_SIZE+1}")
            .one_or_none()
        )
        self.assertIsNotNone(model1)

        # Revert data changes
        self.appbuilder.get_session.delete(model1)
        self.appbuilder.get_session.commit()

        # Verify write links are on the UI
        rv = client.get("/model1permoverride/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("/model1permoverride/delete/1", data)
        self.assertIn("/model1permoverride/add", data)
        self.assertIn("/model1permoverride/edit/1", data)
        self.assertIn("/model1permoverride/show/1", data)

        # Delete write permission from Test Role
        role = self.appbuilder.sm.find_role("Test")
        pvm_write = self.appbuilder.sm.find_permission_view_menu(
            "can_write", "Model1PermOverride"
        )
        self.appbuilder.sm.del_permission_role(role, pvm_write)

        # Unauthorized delete
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string=f"test1")
            .one_or_none()
        )
        pk = model1.id
        rv = client.get(f"/model1permoverride/delete/{pk}")
        self.assertEqual(rv.status_code, 302)
        model = self.db.session.query(Model1).filter_by(id=pk).one_or_none()
        self.assertEqual(model.field_string, "test1")

        # Verify write links are gone from UI
        rv = client.get("/model1permoverride/list/")
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertNotIn("/model1permoverride/delete/1", data)
        self.assertNotIn("/model1permoverride/add/", data)
        self.assertNotIn("/model1permoverride/edit/1", data)
        self.assertIn("/model1permoverride/show/1", data)

        # Revert data changes
        self.appbuilder.get_session.delete(self.appbuilder.sm.find_role("Test"))
        self.appbuilder.get_session.commit()

    def test_action_permission_override(self):
        """
            MVC: Test action permission name override
        """
        from flask_appbuilder import action, ModelView
        from flask_appbuilder.models.sqla.interface import SQLAInterface

        class Model1PermOverride(ModelView):
            datamodel = SQLAInterface(Model1)
            method_permission_name = {
                "list": "read",
                "show": "read",
                "edit": "write",
                "add": "write",
                "delete": "write",
                "download": "read",
                "api_readvalues": "read",
                "api_column_edit": "write",
                "api_column_add": "write",
                "api_delete": "write",
                "api_update": "write",
                "api_create": "write",
                "api_get": "read",
                "api_read": "read",
                "api": "read",
                "action_one": "write",
            }

            @action("action1", "Action1", "", "fa-lock", multiple=True)
            def action_one(self, item):
                return "ACTION ONE"

        self.model1permoverride = Model1PermOverride
        self.appbuilder.add_view_no_menu(Model1PermOverride)

        # Add a user and login before enabling CSRF
        role = self.appbuilder.sm.add_role("Test")
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )
        pvm_read = self.appbuilder.sm.find_permission_view_menu(
            "can_read", "Model1PermOverride"
        )
        pvm_write = self.appbuilder.sm.find_permission_view_menu(
            "can_write", "Model1PermOverride"
        )
        self.appbuilder.sm.add_permission_role(role, pvm_read)
        self.appbuilder.sm.add_permission_role(role, pvm_write)

        client = self.app.test_client()
        self.browser_login(client, "test", "test")

        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model1.id
        rv = client.get(f"/model1permoverride/action/action1/{pk}")
        self.assertEqual(rv.status_code, 200)

        # Delete write permission from Test Role
        role = self.appbuilder.sm.find_role("Test")
        pvm_write = self.appbuilder.sm.find_permission_view_menu(
            "can_write", "Model1PermOverride"
        )
        self.appbuilder.sm.del_permission_role(role, pvm_write)

        rv = client.get("/model1permoverride/action/action1/1")
        self.assertEqual(rv.status_code, 302)

    def test_permission_converge_compress(self):
        """
            MVC: Test permission name converge compress
        """
        from flask_appbuilder import ModelView
        from flask_appbuilder.models.sqla.interface import SQLAInterface

        class Model1PermConverge(ModelView):
            datamodel = SQLAInterface(Model1)
            class_permission_name = "view2"
            previous_class_permission_name = "Model1View"
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
                "api": "access",
            }

        self.appbuilder.add_view_no_menu(Model1PermConverge)
        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_list", "Model1View")
        self.appbuilder.sm.add_permission_role(role, pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu("can_add", "Model1View")
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

        target_state_transitions = {
            "add": {
                ("Model1View", "can_edit"): {("view2", "can_access")},
                ("Model1View", "can_add"): {("view2", "can_access")},
                ("Model1View", "can_list"): {("view2", "can_access")},
                ("Model1View", "can_download"): {("view2", "can_access")},
                ("Model1View", "can_show"): {("view2", "can_access")},
                ("Model1View", "can_delete"): {("view2", "can_access")},
            },
            "del_role_pvm": {
                ("Model1View", "can_show"),
                ("Model1View", "can_add"),
                ("Model1View", "can_download"),
                ("Model1View", "can_list"),
                ("Model1View", "can_edit"),
                ("Model1View", "can_delete"),
            },
            "del_views": {"Model1View"},
            "del_perms": set(),
        }
        state_transitions = self.appbuilder.security_converge()
        self.assertEqual(state_transitions, target_state_transitions)
        role = self.appbuilder.sm.find_role("Test")
        self.assertEqual(len(role.permissions), 1)
