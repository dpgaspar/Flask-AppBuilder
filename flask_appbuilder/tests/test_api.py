import json
import logging
import os

from flask_appbuilder import ModelRestApi, SQLA
from flask_appbuilder.const import (
    API_ADD_COLUMNS_RES_KEY,
    API_ADD_COLUMNS_RIS_KEY,
    API_ADD_TITLE_RIS_KEY,
    API_DESCRIPTION_COLUMNS_RES_KEY,
    API_DESCRIPTION_COLUMNS_RIS_KEY,
    API_EDIT_COLUMNS_RES_KEY,
    API_EDIT_COLUMNS_RIS_KEY,
    API_EDIT_TITLE_RIS_KEY,
    API_FILTERS_RIS_KEY,
    API_LABEL_COLUMNS_RES_KEY,
    API_LABEL_COLUMNS_RIS_KEY,
    API_LIST_COLUMNS_RES_KEY,
    API_LIST_COLUMNS_RIS_KEY,
    API_LIST_TITLE_RIS_KEY,
    API_ORDER_COLUMNS_RIS_KEY,
    API_PERMISSIONS_RES_KEY,
    API_PERMISSIONS_RIS_KEY,
    API_RESULT_RES_KEY,
    API_SECURITY_ACCESS_TOKEN_KEY,
    API_SELECT_COLUMNS_RIS_KEY,
    API_SELECT_KEYS_RIS_KEY,
    API_SHOW_COLUMNS_RIS_KEY,
    API_SHOW_TITLE_RIS_KEY,
    API_URI_RIS_KEY,
)
from flask_appbuilder.models.sqla.filters import FilterGreater, FilterSmaller
from flask_appbuilder.models.sqla.interface import SQLAInterface
import prison
from sqlalchemy.sql.expression import func

from .base import FABTestCase
from .const import (
    MAX_PAGE_SIZE,
    MODEL1_DATA_SIZE,
    MODEL2_DATA_SIZE,
    PASSWORD_ADMIN,
    PASSWORD_READONLY,
    USERNAME_ADMIN,
    USERNAME_READONLY,
)
from .sqla.models import (
    insert_model1,
    insert_model2,
    Model1,
    Model2,
    Model4,
    ModelMMChild,
    ModelMMParent,
    ModelMMParentRequired,
    ModelWithEnums,
    ModelWithProperty,
    TmpEnum,
    validate_name,
)


log = logging.getLogger(__name__)


class APICSRFTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_wtf import CSRFProtect
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.csrf = CSRFProtect(self.app)
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_auth_login(self):
        """
            REST Api: Test auth login CSRF
        """
        client = self.app.test_client()
        rv = self._login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        self.assertEqual(rv.status_code, 200)
        assert json.loads(rv.data.decode("utf-8")).get(
            API_SECURITY_ACCESS_TOKEN_KEY, False
        )


class APIDisableSecViewTestCase(FABTestCase):

    base_fab_endpoint = [
        "IndexView.index",
        "appbuilder.static",
        "static",
        "LocaleView.index",
        "UtilView.back",
        "MenuApi.get_menu_data",
    ]

    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["FAB_ADD_SECURITY_VIEWS"] = False

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_disabled_security_views(self):
        """
            REST Api: Test disabled security views
        """
        for rule in self.appbuilder.get_app.url_map.iter_rules():
            self.assertIn(rule.endpoint, self.base_fab_endpoint)


class APITestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.models.sqla.interface import SQLAInterface
        from flask_appbuilder.api import (
            BaseApi,
            ModelRestApi,
            protect,
            expose,
            rison,
            safe,
        )

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["FAB_API_MAX_PAGE_SIZE"] = MAX_PAGE_SIZE

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        rison_schema = {
            "type": "object",
            "required": ["number"],
            "properties": {"number": {"type": "number"}},
        }

        class Base1Api(BaseApi):
            @expose("/test1")
            @protect()
            @safe
            @rison(rison_schema)
            def test1(self, **kwargs):
                return self.response(200, message=f"{kwargs['rison']['number'] + 1}")

            @expose("/test2")
            @protect()
            @safe
            def test2(self, **kwargs):
                raise Exception

        self.appbuilder.add_api(Base1Api)

        class Model1Api(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            list_columns = [
                "field_integer",
                "field_float",
                "field_string",
                "field_date",
            ]
            description_columns = {
                "field_integer": "Field Integer",
                "field_float": "Field Float",
                "field_string": "Field String",
            }

        self.model1api = Model1Api
        self.appbuilder.add_api(Model1Api)

        class Model1ApiFieldsInfo(Model1Api):
            datamodel = SQLAInterface(Model1)
            add_columns = ["field_integer", "field_float", "field_string", "field_date"]
            edit_columns = ["field_string", "field_integer"]

        self.model1apifieldsinfo = Model1ApiFieldsInfo
        self.appbuilder.add_api(Model1ApiFieldsInfo)

        class Model1FuncApi(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            list_columns = [
                "field_integer",
                "field_float",
                "field_string",
                "field_date",
                "full_concat",
            ]
            description_columns = {
                "field_integer": "Field Integer",
                "field_float": "Field Float",
                "field_string": "Field String",
            }

        self.model1funcapi = Model1Api
        self.appbuilder.add_api(Model1FuncApi)

        class Model1ApiExcludeCols(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            list_exclude_columns = ["field_integer", "field_float", "field_date"]
            show_exclude_columns = list_exclude_columns
            edit_exclude_columns = list_exclude_columns
            add_exclude_columns = list_exclude_columns

        self.appbuilder.add_api(Model1ApiExcludeCols)

        class Model1ApiExcludeRoutes(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            exclude_route_methods = ("info", "delete")

        self.appbuilder.add_api(Model1ApiExcludeRoutes)

        class Model1ApiOrder(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            base_order = ("field_integer", "desc")

        self.appbuilder.add_api(Model1ApiOrder)

        class Model1ApiRestrictedPermissions(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            base_permissions = ["can_get", "can_info"]

        self.appbuilder.add_api(Model1ApiRestrictedPermissions)

        class Model1ApiFiltered(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            base_filters = [
                ["field_integer", FilterGreater, 2],
                ["field_integer", FilterSmaller, 4],
            ]

        self.appbuilder.add_api(Model1ApiFiltered)

        class ModelWithEnumsApi(ModelRestApi):
            datamodel = SQLAInterface(ModelWithEnums)

        self.appbuilder.add_api(ModelWithEnumsApi)

        class Model1BrowserLogin(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            allow_browser_login = True

        self.appbuilder.add_api(Model1BrowserLogin)

        class ModelMMApi(ModelRestApi):
            datamodel = SQLAInterface(ModelMMParent)

        self.appbuilder.add_api(ModelMMApi)

        class ModelMMRequiredApi(ModelRestApi):
            datamodel = SQLAInterface(ModelMMParentRequired)

        self.appbuilder.add_api(ModelMMRequiredApi)

        class Model1CustomValidationApi(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            validators_columns = {"field_string": validate_name}

        self.appbuilder.add_api(Model1CustomValidationApi)

        class Model2Api(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            list_columns = ["group"]
            show_columns = ["group"]

        self.model2api = Model2Api
        self.appbuilder.add_api(Model2Api)

        class Model2DottedNotationApi(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            list_columns = ["field_string", "group.field_string"]
            show_columns = list_columns

        self.appbuilder.add_api(Model2DottedNotationApi)

        class Model2ApiFilteredRelFields(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            list_columns = ["group"]
            show_columns = ["group"]
            add_query_rel_fields = {
                "group": [
                    ["field_integer", FilterGreater, 2],
                    ["field_integer", FilterSmaller, 4],
                ]
            }
            edit_query_rel_fields = add_query_rel_fields

        self.model2apifilteredrelfields = Model2ApiFilteredRelFields
        self.appbuilder.add_api(Model2ApiFilteredRelFields)

        class Model1PermOverride(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            class_permission_name = "api"
            method_permission_name = {
                "get_list": "access",
                "get": "access",
                "put": "access",
                "post": "access",
                "delete": "access",
                "info": "access",
            }

        self.model1permoverride = Model1PermOverride
        self.appbuilder.add_api(Model1PermOverride)

        class ModelWithPropertyApi(ModelRestApi):
            datamodel = SQLAInterface(ModelWithProperty)
            list_columns = ["field_string", "custom_property"]

        self.model1permoverride = ModelWithPropertyApi
        self.appbuilder.add_api(ModelWithPropertyApi)

        class Model1ApiIncludeRoutes(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            include_route_methods = "get"

        self.appbuilder.add_api(Model1ApiIncludeRoutes)

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_babel(self):
        """
            REST Api: Test babel simple test
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1api/?_l_=en"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_babel_wrong_language(self):
        """
            REST Api: Test babel with a wrong language
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1api/?_l_=xx"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_auth_login(self):
        """
            REST Api: Test auth login
        """
        client = self.app.test_client()
        rv = self._login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        self.assertEqual(rv.status_code, 200)
        assert json.loads(rv.data.decode("utf-8")).get(
            API_SECURITY_ACCESS_TOKEN_KEY, False
        )

    def test_auth_login_failed(self):
        """
            REST Api: Test auth login failed
        """
        client = self.app.test_client()
        rv = self._login(client, "fail", "fail")
        self.assertEqual(json.loads(rv.data), {"message": "Not authorized"})
        self.assertEqual(rv.status_code, 401)

    def test_auth_login_bad(self):
        """
            REST Api: Test auth login bad request
        """
        client = self.app.test_client()
        rv = client.post("api/v1/security/login", data="BADADATA")
        self.assertEqual(rv.status_code, 400)

    def test_auth_authorization_browser(self):
        """
            REST Api: Test auth with browser login
        """
        client = self.app.test_client()
        rv = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        # Test access with browser login
        uri = "api/v1/model1browserlogin/1"
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 200)
        # Test unauthorized access with browser login
        uri = "api/v1/model1api/1"
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 401)
        # Test access wihout cookie or JWT
        rv = self.browser_logout(client)
        # Test access with browser login
        uri = "api/v1/model1browserlogin/1"
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 401)
        # Test access with JWT but without cookie
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1browserlogin/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_auth_authorization(self):
        """
            REST Api: Test auth base limited authorization
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        # Test unauthorized DELETE
        pk = 1
        uri = "api/v1/model1apirestrictedpermissions/{}".format(pk)
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 401)
        # Test unauthorized POST
        item = dict(
            field_string="test{}".format(MODEL1_DATA_SIZE + 1),
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1apirestrictedpermissions/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 401)
        # Test authorized GET
        uri = "api/v1/model1apirestrictedpermissions/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_auth_builtin_roles(self):
        """
            REST Api: Test auth readonly builtin role
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_READONLY, PASSWORD_READONLY)
        # Test unauthorized DELETE
        pk = 1
        uri = "api/v1/model1api/{}".format(pk)
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 401)

        # Test unauthorized POST
        item = dict(
            field_string="test{}".format(MODEL1_DATA_SIZE + 1),
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1api/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 401)

        # Test authorized GET
        uri = "api/v1/model1api/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        # Test authorized INFO
        uri = "api/v1/model1api/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_base_rison_argument(self):
        """
            REST Api: Test not a valid rison argument
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1api/?{}={}".format(API_URI_RIS_KEY, "(columns!(not_valid))")
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data, {"message": "Not a valid rison/json argument"})
        uri = "api/v1/model1api/1?{}={}".format(
            API_URI_RIS_KEY, "(columns!(not_valid))"
        )
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data, {"message": "Not a valid rison/json argument"})

    def test_base_rison_schema(self):
        """
            REST Api: Test rison schema validation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        arguments = {"number": 1}
        uri = "api/v1/base1api/test1?{}={}".format(
            API_URI_RIS_KEY, prison.dumps(arguments)
        )
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data, {"message": "2"})

        # Rison Schema type validation
        arguments = {"number": "1"}
        uri = "api/v1/base1api/test1?{}={}".format(
            API_URI_RIS_KEY, prison.dumps(arguments)
        )
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

        # Rison Schema validation required field
        arguments = {"numbers": 1}
        uri = "api/v1/base1api/test1?{}={}".format(
            API_URI_RIS_KEY, prison.dumps(arguments)
        )
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

    def test_base_safe(self):
        """
            REST Api: Test safe decorator 500
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/base1api/test2"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 500)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data, {"message": "Fatal error"})

    def test_exclude_route_methods(self):
        """
            REST Api: Test exclude route methods
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1apiexcluderoutes/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 405)

        uri = "api/v1/model1apiexcluderoutes/1"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 405)

        # Check that permissions do not exist
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_info", "Model1ApiExcludeRoutes"
        )
        self.assertIsNone(pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_delete", "Model1ApiExcludeRoutes"
        )
        self.assertIsNone(pvm)

    def test_include_route_methods(self):
        """
            REST Api: Test include route methods
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1apiincluderoutes/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/model1apiincluderoutes/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        # Check that permissions do not exist
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_info", "Model1ApiIncludeRoutes"
        )
        self.assertIsNone(pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_put", "Model1ApiIncludeRoutes"
        )
        self.assertIsNone(pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_post", "Model1ApiIncludeRoutes"
        )
        self.assertIsNone(pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_delete", "Model1ApiIncludeRoutes"
        )
        self.assertIsNone(pvm)

    def test_get_item(self):
        """
            REST Api: Test get item
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        for i in range(1, MODEL1_DATA_SIZE):
            rv = self.auth_client_get(client, token, "api/v1/model1api/{}".format(i))
            data = json.loads(rv.data.decode("utf-8"))
            self.assertEqual(rv.status_code, 200)
            self.assert_get_item(rv, data, i - 1)

    def assert_get_item(self, rv, data, value):
        self.assertEqual(
            data[API_RESULT_RES_KEY],
            {
                "field_date": None,
                "field_float": float(value),
                "field_integer": value,
                "field_string": "test{}".format(value),
            },
        )
        # test descriptions
        self.assertEqual(
            data["description_columns"], self.model1api.description_columns
        )
        # test labels
        self.assertEqual(
            data[API_LABEL_COLUMNS_RES_KEY],
            {
                "field_date": "Field Date",
                "field_float": "Field Float",
                "field_integer": "Field Integer",
                "field_string": "Field String",
            },
        )
        self.assertEqual(rv.status_code, 200)

    def test_get_item_select_cols(self):
        """
            REST Api: Test get item with select columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        for i in range(1, MODEL1_DATA_SIZE):
            uri = "api/v1/model1api/{}?q=({}:!(field_integer))".format(
                i, API_SELECT_COLUMNS_RIS_KEY
            )
            rv = self.auth_client_get(client, token, uri)
            data = json.loads(rv.data.decode("utf-8"))
            self.assertEqual(data[API_RESULT_RES_KEY], {"field_integer": i - 1})
            self.assertEqual(
                data[API_DESCRIPTION_COLUMNS_RES_KEY],
                {"field_integer": "Field Integer"},
            )
            self.assertEqual(
                data[API_LABEL_COLUMNS_RES_KEY], {"field_integer": "Field Integer"}
            )
            self.assertEqual(rv.status_code, 200)

    def test_get_item_dotted_notation(self):
        """
            REST Api: Test get item with dotted notation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model2 = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model2.id
        uri = f"api/v1/model2dottednotationapi/{pk}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY],
            {"field_string": "test0", "group": {"field_string": "test0"}},
        )
        self.assertEqual(rv.status_code, 200)

    def test_get_item_select_meta_data(self):
        """
            REST Api: Test get item select meta data
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        selectable_keys = [
            API_DESCRIPTION_COLUMNS_RIS_KEY,
            API_LABEL_COLUMNS_RIS_KEY,
            API_SHOW_COLUMNS_RIS_KEY,
            API_SHOW_TITLE_RIS_KEY,
        ]
        for selectable_key in selectable_keys:
            argument = {API_SELECT_KEYS_RIS_KEY: [selectable_key]}
            uri = "api/v1/model1api/1?{}={}".format(
                API_URI_RIS_KEY, prison.dumps(argument)
            )
            rv = self.auth_client_get(client, token, uri)
            data = json.loads(rv.data.decode("utf-8"))
            self.assertEqual(len(data.keys()), 1 + 2)  # always exist id, result
            # We assume that rison meta key equals result meta key
            assert selectable_key in data

    def test_get_item_excluded_cols(self):
        """
            REST Api: Test get item with excluded columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        pk = 1
        rv = self.auth_client_get(
            client, token, "api/v1/model1apiexcludecols/{}".format(pk)
        )
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data[API_RESULT_RES_KEY], {"field_string": "test0"})
        self.assertEqual(rv.status_code, 200)

    def test_get_item_not_found(self):
        """
            REST Api: Test get item not found
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        pk = MODEL1_DATA_SIZE + 1
        rv = self.auth_client_get(client, token, "api/v1/model1api/{}".format(pk))
        self.assertEqual(rv.status_code, 404)

    def test_get_item_base_filters(self):
        """
            REST Api: Test get item with base filters
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # We can't get a base filtered item
        pk = 1
        rv = self.auth_client_get(
            client, token, "api/v1/model1apifiltered/{}".format(pk)
        )
        self.assertEqual(rv.status_code, 404)
        # This one is ok pk=4 field_integer=3 2>3<4
        pk = 4
        rv = self.auth_client_get(client, token, f"api/v1/model1apifiltered/{pk}")
        self.assertEqual(rv.status_code, 200)

    def test_get_item_1m_field(self):
        """
            REST Api: Test get item with 1-N related field
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # We can't get a base filtered item
        model2 = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model2.id
        rv = self.auth_client_get(client, token, f"api/v1/model2api/{pk}")
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 200)
        expected_rel_field = {
            "group": {
                "field_date": None,
                "field_float": 0.0,
                "field_integer": 0,
                "field_string": "test0",
                "id": 1,
            }
        }
        self.assertEqual(data[API_RESULT_RES_KEY], expected_rel_field)

    def test_get_item_mm_field(self):
        """
            REST Api: Test get item with N-N related field
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # We can't get a base filtered item
        pk = 1
        rv = self.auth_client_get(client, token, "api/v1/modelmmapi/{}".format(pk))
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 200)
        expected_rel_field = [
            {"field_string": "1", "id": 1},
            {"field_string": "2", "id": 2},
            {"field_string": "3", "id": 3},
        ]
        self.assertEqual(data[API_RESULT_RES_KEY]["children"], expected_rel_field)

    def test_get_list(self):
        """
            REST Api: Test get list
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        rv = self.auth_client_get(client, token, "api/v1/model1api/")

        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)

    def test_get_list_dotted_notation(self):
        """
            REST Api: Test get list with dotted notation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        arguments = {"order_column": "field_string", "order_direction": "asc"}
        uri = "api/v1/model2dottednotationapi/?{}={}".format(
            API_URI_RIS_KEY, prison.dumps(arguments)
        )
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        i = 0
        self.assertEqual(
            data[API_RESULT_RES_KEY][i],
            {"field_string": "test0", "group": {"field_string": "test0"}},
        )

    def test_get_list_dotted_order(self):
        """
            REST Api: Test get list and order dotted notation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        arguments = {"order_column": "group.field_string", "order_direction": "desc"}
        uri = "api/v1/model2dottednotationapi/?{}={}".format(
            API_URI_RIS_KEY, prison.dumps(arguments)
        )
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        i = 0
        self.assertEqual(
            data[API_RESULT_RES_KEY][i],
            {"field_string": "test9", "group": {"field_string": "test9"}},
        )

    def test_get_list_multiple_dotted_order(self):
        """
            REST Api: Test get list order multiple dotted notation
        """

        class Model4Api(ModelRestApi):
            datamodel = SQLAInterface(Model4)
            list_columns = [
                "field_string",
                "model1_1.field_string",
                "model1_2.field_string",
            ]

        self.appbuilder.add_api(Model4Api)

        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Test order asc for model1_1
        arguments = {"order_column": "model1_1.field_string", "order_direction": "desc"}
        uri = "api/v1/model4api/?{}={}".format(API_URI_RIS_KEY, prison.dumps(arguments))
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        i = 0
        self.assertEqual(
            data[API_RESULT_RES_KEY][i],
            {
                "field_string": "test9",
                "model1_1": {"field_string": "test9"},
                "model1_2": {"field_string": "test9"},
            },
        )

        # Test order desc for model1_2
        arguments = {"order_column": "model1_2.field_string", "order_direction": "asc"}
        uri = "api/v1/model4api/?{}={}".format(API_URI_RIS_KEY, prison.dumps(arguments))
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        i = 0
        self.assertEqual(
            data[API_RESULT_RES_KEY][i],
            {
                "field_string": "test0",
                "model1_1": {"field_string": "test0"},
                "model1_2": {"field_string": "test0"},
            },
        )

    def test_get_list_order(self):
        """
            REST Api: Test get list order params
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # test string order asc
        arguments = {"order_column": "field_integer", "order_direction": "asc"}
        uri = "api/v1/model1api/?{}={}".format(API_URI_RIS_KEY, prison.dumps(arguments))
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": 0.0,
                "field_integer": 0,
                "field_string": "test0",
            },
        )
        self.assertEqual(rv.status_code, 200)
        # test string order desc
        arguments = {"order_column": "field_integer", "order_direction": "desc"}
        uri = "api/v1/model1api/?{}={}".format(API_URI_RIS_KEY, prison.dumps(arguments))
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": float(MODEL1_DATA_SIZE - 1),
                "field_integer": MODEL1_DATA_SIZE - 1,
                "field_string": "test{}".format(MODEL1_DATA_SIZE - 1),
            },
        )
        self.assertEqual(rv.status_code, 200)

    def test_get_list_base_order(self):
        """
            REST Api: Test get list with base order
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # test string order asc
        rv = self.auth_client_get(client, token, "api/v1/model1apiorder/")
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": float(MODEL1_DATA_SIZE - 1),
                "field_integer": MODEL1_DATA_SIZE - 1,
                "field_string": "test{}".format(MODEL1_DATA_SIZE - 1),
            },
        )
        # Test override
        arguments = {"order_column": "field_integer", "order_direction": "asc"}
        uri = f"api/v1/model1apiorder/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": 0.0,
                "field_integer": 0,
                "field_string": "test0",
            },
        )

    def test_get_list_page(self):
        """
            REST Api: Test get list page params
        """
        page_size = 5
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # test page zero
        arguments = {
            "page_size": page_size,
            "page": 0,
            "order_column": "field_integer",
            "order_direction": "asc",
        }
        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": 0.0,
                "field_integer": 0,
                "field_string": "test0",
            },
        )
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(data[API_RESULT_RES_KEY]), page_size)
        # test page one
        arguments = {
            "page_size": page_size,
            "page": 1,
            "order_column": "field_integer",
            "order_direction": "asc",
        }
        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)

        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY][0],
            {
                "field_date": None,
                "field_float": float(page_size),
                "field_integer": page_size,
                "field_string": "test{}".format(page_size),
            },
        )
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(data[API_RESULT_RES_KEY]), page_size)

        # test simple page test, mainly because of MSSQL dialect
        arguments = {"page_size": page_size, "page": 1}
        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEquals(rv.status_code, 200)

    def test_get_list_max_page_size(self):
        """
            REST Api: Test get list max page size config setting
        """
        page_size = 200  # Max is globally set to MAX_PAGE_SIZE
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # test page zero
        arguments = {
            "page_size": page_size,
            "page": 0,
            "order_column": "field_integer",
            "order_direction": "asc",
        }
        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(len(data[API_RESULT_RES_KEY]), MAX_PAGE_SIZE)

    def test_get_list_max_page_size_override(self):
        """
            REST Api: Test get list max page size property override
        """

        class Model1PageSizeOverride(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            max_page_size = -1
            list_columns = [
                "field_integer",
                "field_float",
                "field_string",
                "field_date",
            ]
            description_columns = {
                "field_integer": "Field Integer",
                "field_float": "Field Float",
                "field_string": "Field String",
            }

        self.model1api = Model1PageSizeOverride
        self.appbuilder.add_api(Model1PageSizeOverride)

        page_size = 200  # Max is globally set to MAX_PAGE_SIZE
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # test page zero
        arguments = {
            "page_size": page_size,
            "page": 0,
            "order_column": "field_integer",
            "order_direction": "asc",
        }
        endpoint = "api/v1/model1pagesizeoverride/"
        uri = f"{endpoint}?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(len(data[API_RESULT_RES_KEY]), MODEL1_DATA_SIZE)

    def test_get_list_filters(self):
        """
            REST Api: Test get list filter params
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        filter_value = 5
        # test string order asc
        arguments = {
            API_FILTERS_RIS_KEY: [
                {"col": "field_integer", "opr": "gt", "value": filter_value}
            ],
            "order_column": "field_integer",
            "order_direction": "asc",
        }

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        expected_result = {
            "field_date": None,
            "field_float": float(filter_value + 1),
            "field_integer": filter_value + 1,
            "field_string": "test{}".format(filter_value + 1),
        }
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data[API_RESULT_RES_KEY][0], expected_result)
        self.assertEqual(rv.status_code, 200)

        # Test with JSON encode content
        from urllib.parse import quote

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={quote(json.dumps(arguments))}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data[API_RESULT_RES_KEY][0], expected_result)
        self.assertEqual(rv.status_code, 200)

    def test_get_list_invalid_filters(self):
        """
            REST Api: Test get list filter params
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        arguments = {API_FILTERS_RIS_KEY: [{"col": "field_integer", "opr": "gt"}]}

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

    def test_get_list_filters_m_m(self):
        """
            REST Api: Test get list filter params with many to many
        """
        session = self.appbuilder.get_session

        child = ModelMMChild()
        child.field_string = "test_child_tmp"
        children = [child]
        session.add(child)
        session.commit()
        parent = ModelMMParent()
        parent.field_string = "test_tmp"
        parent.children = children
        session.add(parent)
        session.commit()

        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        arguments = {
            API_FILTERS_RIS_KEY: [{"col": "children", "opr": "rel_m_m", "value": [4]}]
        }

        uri = f"api/v1/modelmmapi/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["result"][0]["children"][0]["field_string"], "test_child_tmp"
        )

        arguments = {
            API_FILTERS_RIS_KEY: [
                {"col": "children", "opr": "rel_m_m", "value": [1, 2]}
            ]
        }

        uri = f"api/v1/modelmmapi/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)

        parent_ = (
            session.query(ModelMMParent)
            .filter_by(field_string="test_tmp")
            .one_or_none()
        )
        child_ = (
            session.query(ModelMMChild)
            .filter_by(field_string="test_child_tmp")
            .one_or_none()
        )

        session.delete(parent_)
        session.commit()
        session.delete(child_)
        session.commit()

    def test_get_list_filters_wrong_col(self):
        """
            REST Api: Test get list with wrong columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        filter_value = "value"
        arguments = {
            API_FILTERS_RIS_KEY: [
                {"col": "wrong_columns", "opr": "sw", "value": filter_value},
                {"col": "field_string", "opr": "sw", "value": filter_value},
            ]
        }

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"

        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

    def test_get_list_filters_wrong_opr(self):
        """
            REST Api: Test get list with wrong operation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        filter_value = 1
        arguments = {
            API_FILTERS_RIS_KEY: [
                {"col": "field_integer", "opr": "sw", "value": filter_value}
            ]
        }

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"

        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

    def test_get_list_filters_wrong_order(self):
        """
            REST Api: Test get list with wrong order column
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        arguments = {"order_column": "wrong_column", "order_direction": "asc"}

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"

        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 400)

    def test_get_list_select_cols(self):
        """
            REST Api: Test get list with selected columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        argument = {
            API_SELECT_COLUMNS_RIS_KEY: ["field_integer"],
            "order_column": "field_integer",
            "order_direction": "asc",
        }

        uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(argument)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data[API_RESULT_RES_KEY][0], {"field_integer": 0})
        self.assertEqual(
            data[API_LABEL_COLUMNS_RES_KEY], {"field_integer": "Field Integer"}
        )
        self.assertEqual(
            data[API_DESCRIPTION_COLUMNS_RES_KEY], {"field_integer": "Field Integer"}
        )
        self.assertEqual(data[API_LIST_COLUMNS_RES_KEY], ["field_integer"])
        self.assertEqual(rv.status_code, 200)

    def test_get_list_select_meta_data(self):
        """
            REST Api: Test get list select meta data
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        selectable_keys = [
            API_DESCRIPTION_COLUMNS_RIS_KEY,
            API_LABEL_COLUMNS_RIS_KEY,
            API_ORDER_COLUMNS_RIS_KEY,
            API_LIST_COLUMNS_RIS_KEY,
            API_LIST_TITLE_RIS_KEY,
        ]
        for selectable_key in selectable_keys:
            argument = {API_SELECT_KEYS_RIS_KEY: [selectable_key]}
            uri = f"api/v1/model1api/?{API_URI_RIS_KEY}={prison.dumps(argument)}"
            rv = self.auth_client_get(client, token, uri)
            data = json.loads(rv.data.decode("utf-8"))
            self.assertEqual(len(data.keys()), 1 + 3)  # always exist count, ids, result
            # We assume that rison meta key equals result meta key
            assert selectable_key in data

    def test_get_list_exclude_cols(self):
        """
            REST Api: Test get list with excluded columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/model1apiexcludecols/"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data[API_RESULT_RES_KEY][0], {"field_string": "test0"})

    def test_get_list_base_filters(self):
        """
            REST Api: Test get list with base filters
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        arguments = {"order_column": "field_integer", "order_direction": "desc"}
        uri = f"api/v1/model1apifiltered/?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_result = [
            {
                "field_date": None,
                "field_float": 3.0,
                "field_integer": 3,
                "field_string": "test3",
            }
        ]
        self.assertEqual(data[API_RESULT_RES_KEY], expected_result)

    def test_info_filters(self):
        """
            REST Api: Test info filters
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1api/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_filters = {
            "field_date": [
                {"name": "Equal to", "operator": "eq"},
                {"name": "Greater than", "operator": "gt"},
                {"name": "Smaller than", "operator": "lt"},
                {"name": "Not Equal to", "operator": "neq"},
            ],
            "field_float": [
                {"name": "Equal to", "operator": "eq"},
                {"name": "Greater than", "operator": "gt"},
                {"name": "Smaller than", "operator": "lt"},
                {"name": "Not Equal to", "operator": "neq"},
            ],
            "field_integer": [
                {"name": "Equal to", "operator": "eq"},
                {"name": "Greater than", "operator": "gt"},
                {"name": "Smaller than", "operator": "lt"},
                {"name": "Not Equal to", "operator": "neq"},
            ],
            "field_string": [
                {"name": "Starts with", "operator": "sw"},
                {"name": "Ends with", "operator": "ew"},
                {"name": "Contains", "operator": "ct"},
                {"name": "Equal to", "operator": "eq"},
                {"name": "Not Starts with", "operator": "nsw"},
                {"name": "Not Ends with", "operator": "new"},
                {"name": "Not Contains", "operator": "nct"},
                {"name": "Not Equal to", "operator": "neq"},
            ],
        }
        self.assertEqual(data["filters"], expected_filters)

    def test_info_fields(self):
        """
            REST Api: Test info fields (add, edit)
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/model1apifieldsinfo/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expect_add_fields = [
            {
                "description": "Field Integer",
                "label": "Field Integer",
                "name": "field_integer",
                "required": False,
                "unique": False,
                "type": "Integer",
            },
            {
                "description": "Field Float",
                "label": "Field Float",
                "name": "field_float",
                "required": False,
                "unique": False,
                "type": "Float",
            },
            {
                "description": "Field String",
                "label": "Field String",
                "name": "field_string",
                "required": True,
                "unique": True,
                "type": "String",
                "validate": ["<Length(min=None, max=50, equal=None, error=None)>"],
            },
            {
                "description": "",
                "label": "Field Date",
                "name": "field_date",
                "required": False,
                "unique": False,
                "type": "Date",
            },
        ]
        expect_edit_fields = list()
        for edit_col in self.model1apifieldsinfo.edit_columns:
            for item in expect_add_fields:
                if item["name"] == edit_col:
                    expect_edit_fields.append(item)
        self.assertEqual(data[API_ADD_COLUMNS_RES_KEY], expect_add_fields)
        self.assertEqual(data[API_EDIT_COLUMNS_RES_KEY], expect_edit_fields)

    def test_info_fields_rel_field(self):
        """
            REST Api: Test info fields with related fields
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/model2api/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_rel_add_field = {
            "count": MODEL2_DATA_SIZE,
            "description": "",
            "label": "Group",
            "name": "group",
            "required": True,
            "unique": False,
            "type": "Related",
            "values": [],
        }
        for i in range(self.model2api.page_size):
            expected_rel_add_field["values"].append(
                {"id": i + 1, "value": "test{}".format(i)}
            )
        for rel_field in data[API_ADD_COLUMNS_RES_KEY]:
            if rel_field["name"] == "group":
                self.assertEqual(rel_field, expected_rel_add_field)

    def test_info_fields_rel_filtered_field(self):
        """
            REST Api: Test info fields with filtered
            related fields
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model2apifilteredrelfields/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_rel_add_field = {
            "description": "",
            "label": "Group",
            "name": "group",
            "required": True,
            "unique": False,
            "type": "Related",
            "count": 1,
            "values": [{"id": 4, "value": "test3"}],
        }
        for rel_field in data[API_ADD_COLUMNS_RES_KEY]:
            if rel_field["name"] == "group":
                self.assertEqual(rel_field, expected_rel_add_field)
        for rel_field in data[API_EDIT_COLUMNS_RES_KEY]:
            if rel_field["name"] == "group":
                self.assertEqual(rel_field, expected_rel_add_field)

    def test_info_permissions(self):
        """
            REST Api: Test info permissions
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1api/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_permissions = [
            "can_delete",
            "can_get",
            "can_info",
            "can_post",
            "can_put",
        ]
        self.assertEqual(sorted(data[API_PERMISSIONS_RES_KEY]), expected_permissions)
        uri = "api/v1/model1apirestrictedpermissions/_info"
        rv = self.auth_client_get(client, token, uri)
        data = json.loads(rv.data.decode("utf-8"))
        expected_permissions = ["can_get", "can_info"]
        self.assertEqual(sorted(data[API_PERMISSIONS_RES_KEY]), expected_permissions)

    def test_info_select_meta_data(self):
        """
            REST Api: Test info select meta data
        """
        # select meta for add fields
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        selectable_keys = [
            API_ADD_COLUMNS_RIS_KEY,
            API_EDIT_COLUMNS_RIS_KEY,
            API_PERMISSIONS_RIS_KEY,
            API_FILTERS_RIS_KEY,
            API_ADD_TITLE_RIS_KEY,
            API_EDIT_TITLE_RIS_KEY,
        ]
        for selectable_key in selectable_keys:
            arguments = {API_SELECT_KEYS_RIS_KEY: [selectable_key]}
            uri = f"api/v1/model1api/_info?{API_URI_RIS_KEY}={prison.dumps(arguments)}"
            rv = self.auth_client_get(client, token, uri)
            data = json.loads(rv.data.decode("utf-8"))
            self.assertEqual(len(data.keys()), 1)
            # We assume that rison meta key equals result meta key
            assert selectable_key in data

    def test_delete_item(self):
        """
            REST Api: Test delete item
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model2)
            .filter_by(field_string="test2")
            .one_or_none()
        )
        pk = model.id
        uri = f"api/v1/model2api/{pk}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model2).get(pk)
        self.assertEqual(model, None)

        # Revert data changes
        insert_model2(self.appbuilder.get_session, i=pk - 1)

    def test_delete_item_integrity(self):
        """
            REST Api: Test delete item integrity
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model.id
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 422)
        model = self.db.session.query(Model1).get(pk)
        self.assertIsNotNone(model)

    def test_delete_item_not_found(self):
        """
            REST Api: Test delete item not found
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        max_id = self.appbuilder.get_session.query(func.max(Model1.id)).scalar()
        pk = max_id + 1
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 404)

    def test_delete_item_base_filters(self):
        """
            REST Api: Test delete item with base filters
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_integer=2)
            .one_or_none()
        )

        # Try to delete a filtered item
        pk = model.id
        uri = "api/v1/model1apifiltered/{}".format(pk)
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 404)

    def test_update_item(self):
        """
            REST Api: Test update item
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test2")
            .one_or_none()
        )
        pk = model1.id
        item = dict(field_string="test_Put", field_integer=0, field_float=0.0)
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model1).get(pk)
        self.assertEqual(model.field_string, "test_Put")
        self.assertEqual(model.field_integer, 0)
        self.assertEqual(model.field_float, 0.0)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=pk - 1)

    def test_update_custom_validation(self):
        """
            REST Api: Test update item custom validation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test2")
            .one_or_none()
        )
        pk = model1.id
        item = dict(field_string="test_Put", field_integer=0, field_float=0.0)
        uri = f"api/v1/model1customvalidationapi/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        pk = 3
        item = dict(field_string="Atest_Put", field_integer=0, field_float=0.0)
        uri = f"api/v1/model1customvalidationapi/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 200)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=pk - 1)

    def test_update_item_base_filters(self):
        """
            REST Api: Test update item with base filters
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_integer=3)
            .one_or_none()
        )
        pk = model1.id
        item = dict(field_string="test_Put", field_integer=3, field_float=3.0)
        uri = f"api/v1/model1apifiltered/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model1).get(pk)
        self.assertEqual(model.field_string, "test_Put")
        self.assertEqual(model.field_integer, 3)
        self.assertEqual(model.field_float, 3.0)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=pk - 1)

        # We can't update an item that is base filtered
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_integer=1)
            .one_or_none()
        )
        pk = model1.id
        uri = f"api/v1/model1apifiltered/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 404)

    def test_update_item_not_found(self):
        """
            REST Api: Test update item not found
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        max_id = self.appbuilder.get_session.query(func.max(Model1.id)).scalar()
        pk = max_id + 1
        item = dict(field_string="test_Put", field_integer=0, field_float=0.0)
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 404)

    def test_update_val_size(self):
        """
            REST Api: Test update validate size
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string=f"test0")
            .one_or_none()
        )
        pk = model1.id
        field_string = "a" * 51
        item = dict(field_string=field_string, field_integer=11, field_float=11.0)
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data["message"]["field_string"][0], "Longer than maximum length 50."
        )

    def test_update_mm_field(self):
        """
            REST Api: Test update m-m field
        """
        session = self.appbuilder.get_session
        pk = 1
        # Fetching children so that we can revert the changes
        original_model = session.query(ModelMMParent).filter_by(id=pk).one_or_none()
        original_children = [child for child in original_model.children]

        child = ModelMMChild()
        child.field_string = "update_m,m"
        session.add(child)
        session.commit()

        child_id = (
            session.query(ModelMMChild)
            .filter_by(field_string="update_m,m")
            .one_or_none()
            .id
        )
        item = dict(children=[child_id])
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/modelmmapi/{}".format(pk)
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY], {"children": [child_id], "field_string": "0"}
        )

        # Revert data changes
        original_model = session.query(ModelMMParent).filter_by(id=pk).one_or_none()
        original_model.children = original_children
        session.merge(original_model)
        session.commit()
        child = session.query(ModelMMChild).filter_by(id=child_id).one_or_none()
        session.delete(child)
        session.commit()

    def test_update_item_val_type(self):
        """
            REST Api: Test update validate type
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model1.id
        item = dict(
            field_string=f"test{MODEL1_DATA_SIZE + 1}",
            field_integer=f"test{MODEL1_DATA_SIZE + 1}",
            field_float=11.0,
        )
        uri = f"api/v1/model1api/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["message"]["field_integer"][0], "Not a valid integer.")

        item = dict(field_string=11, field_integer=11, field_float=11.0)
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["message"]["field_string"][0], "Not a valid string.")

    def test_update_item_excluded_cols(self):
        """
            REST Api: Test update item with excluded cols
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        model1 = (
            self.appbuilder.get_session.query(Model1)
            .filter_by(field_string="test0")
            .one_or_none()
        )
        pk = model1.id
        item = dict(field_string="test_Put", field_integer=1000)
        uri = f"api/v1/model1apiexcludecols/{pk}"
        rv = self.auth_client_put(client, token, uri, item)
        self.assertEqual(rv.status_code, 200)
        model = self.db.session.query(Model1).get(pk)
        self.assertEqual(model.field_integer, 0)
        self.assertEqual(model.field_float, 0.0)
        self.assertEqual(model.field_date, None)

        # Revert data changes
        insert_model1(self.appbuilder.get_session, i=pk - 1)

    def test_create_item(self):
        """
            REST Api: Test create item
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(
            field_string="test{}".format(MODEL1_DATA_SIZE + 1),
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1api/"
        rv = self.auth_client_post(client, token, uri, item)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data[API_RESULT_RES_KEY], item)
        model = (
            self.db.session.query(Model1)
            .filter_by(field_string="test{}".format(MODEL1_DATA_SIZE + 1))
            .first()
        )
        self.assertEqual(model.field_string, f"test{MODEL1_DATA_SIZE + 1}")
        self.assertEqual(model.field_integer, MODEL1_DATA_SIZE + 1)
        self.assertEqual(model.field_float, float(MODEL1_DATA_SIZE + 1))

        # Revert data changes
        self.appbuilder.get_session.delete(model)
        self.appbuilder.get_session.commit()

    def test_create_item_bad_request(self):
        """
            REST Api: Test create item with bad request
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(
            field_string="test{}".format(MODEL1_DATA_SIZE + 1),
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1api/"
        rv = client.post(
            uri, data=item, headers={"Authorization": "Bearer {}".format(token)}
        )
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(data, {"message": "Request is not JSON"})

    def test_create_item_custom_validation(self):
        """
            REST Api: Test create item custom validation
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(
            field_string=f"test{MODEL1_DATA_SIZE + 1}",
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1customvalidationapi/"
        rv = self.auth_client_post(client, token, uri, item)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 422)
        self.assertEqual(
            data, {"message": {"field_string": ["Name must start with an A"]}}
        )
        item = dict(
            field_string=f"A{MODEL1_DATA_SIZE + 1}",
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        rv = self.auth_client_post(client, token, uri, item)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 201)

        # Revert test data
        self.appbuilder.get_session.query(Model1).filter_by(
            field_string=f"A{MODEL1_DATA_SIZE + 1}"
        ).delete()
        self.appbuilder.get_session.commit()

    def test_create_item_custom_schema(self):
        """
            REST Api: Test create item custom schema
        """
        from .sqla.models import Model1CustomSchema

        class Model1ApiCustomSchema(self.model1api):
            add_model_schema = Model1CustomSchema()

        self.appbuilder.add_api(Model1ApiCustomSchema)

        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(
            field_string=f"test{MODEL1_DATA_SIZE + 1}",
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
            field_date=None,
        )
        uri = "api/v1/model1customvalidationapi/"
        rv = self.auth_client_post(client, token, uri, item)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 422)
        self.assertEqual(
            data, {"message": {"field_string": ["Name must start with an A"]}}
        )

    def test_create_item_val_size(self):
        """
            REST Api: Test create validate size
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        field_string = "a" * 51
        item = dict(
            field_string=field_string,
            field_integer=MODEL1_DATA_SIZE + 1,
            field_float=float(MODEL1_DATA_SIZE + 1),
        )
        uri = "api/v1/model1api/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data["message"]["field_string"][0], "Longer than maximum length 50."
        )

    def test_create_item_val_type(self):
        """
            REST Api: Test create validate type
        """
        # Test integer as string
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(
            field_string=f"test{MODEL1_DATA_SIZE}",
            field_integer=f"test{MODEL1_DATA_SIZE}",
            field_float=float(MODEL1_DATA_SIZE),
        )
        uri = "api/v1/model1api/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["message"]["field_integer"][0], "Not a valid integer.")
        # Test string as integer
        item = dict(
            field_string=MODEL1_DATA_SIZE,
            field_integer=MODEL1_DATA_SIZE,
            field_float=float(MODEL1_DATA_SIZE),
        )
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(data["message"]["field_string"][0], "Not a valid string.")

    def test_create_item_excluded_cols(self):
        """
            REST Api: Test create with excluded columns
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(field_string=f"test{MODEL1_DATA_SIZE + 1}")
        uri = "api/v1/model1apiexcludecols/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 201)
        item = dict(
            field_string="test{}".format(MODEL1_DATA_SIZE + 2),
            field_integer=MODEL1_DATA_SIZE + 2,
        )
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 201)
        model = (
            self.db.session.query(Model1)
            .filter_by(field_string=f"test{MODEL1_DATA_SIZE + 1}")
            .first()
        )
        self.assertEqual(model.field_integer, None)
        self.assertEqual(model.field_float, None)
        self.assertEqual(model.field_date, None)

        # Revert test data
        self.appbuilder.get_session.query(Model1).filter_by(
            field_string=f"test{MODEL1_DATA_SIZE + 1}"
        ).delete()
        self.appbuilder.get_session.query(Model1).filter_by(
            field_string=f"test{MODEL1_DATA_SIZE + 2}"
        ).delete()
        self.appbuilder.get_session.commit()

    def test_create_item_with_enum(self):
        """
            REST Api: Test create item with enum
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(enum2="e1")
        uri = "api/v1/modelwithenumsapi/"
        rv = self.auth_client_post(client, token, uri, item)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(rv.status_code, 201)
        model = self.db.session.query(ModelWithEnums).get(data["id"])
        self.assertEqual(model.enum2, TmpEnum.e1)

        # Revert test data
        self.appbuilder.get_session.query(Model1).filter_by(
            field_string=f"test{MODEL1_DATA_SIZE + 1}"
        ).delete()
        self.appbuilder.get_session.query(Model1).filter_by(
            field_string=f"test{MODEL1_DATA_SIZE + 2}"
        ).delete()
        self.appbuilder.get_session.commit()

    def test_create_item_mm_field(self):
        """
            REST Api: Test create with M-M field
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        item = dict(field_string="new1", children=[1, 2])
        uri = "api/v1/modelmmapi/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY], {"children": [1, 2], "field_string": "new1"}
        )
        # Test without M-M field data, default is not required
        item = dict(field_string="new2")
        uri = "api/v1/modelmmapi/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data[API_RESULT_RES_KEY], {"children": [], "field_string": "new2"}
        )
        # Test without M-M field data, default is required
        item = dict(field_string="new1")
        uri = "api/v1/modelmmrequiredapi/"
        rv = self.auth_client_post(client, token, uri, item)
        self.assertEqual(rv.status_code, 422)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(
            data, {"message": {"children": ["Missing data for required field."]}}
        )

        # Rollback data changes
        model1 = (
            self.appbuilder.get_session.query(ModelMMParent)
            .filter_by(field_string="new1")
            .one_or_none()
        )
        model2 = (
            self.appbuilder.get_session.query(ModelMMParent)
            .filter_by(field_string="new2")
            .one_or_none()
        )
        self.appbuilder.get_session.delete(model1)
        self.appbuilder.get_session.delete(model2)
        self.appbuilder.get_session.commit()

    def test_get_list_col_function(self):
        """
            REST Api: Test get list of objects with columns as functions
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/model1funcapi/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        for i in range(1, self.model1api.page_size):
            item = data[API_RESULT_RES_KEY][i - 1]
            self.assertEqual(
                item["full_concat"], f"test{str(i - 1)}.{i - 1}.{float(i - 1)}.{None}"
            )

    def test_get_list_col_property(self):
        """
            REST Api: Test get list of objects with columns as property
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/modelwithpropertyapi/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        # Tests count property
        self.assertEqual(data["count"], MODEL1_DATA_SIZE)
        # Tests data result default page size
        self.assertEqual(len(data[API_RESULT_RES_KEY]), self.model1api.page_size)
        for i in range(1, self.model1api.page_size):
            item = data[API_RESULT_RES_KEY][i - 1]
            self.assertEqual(item["custom_property"], f"{item['field_string']}_custom")

    def test_openapi(self):
        """
            REST Api: Test OpenAPI spec
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/_openapi"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_swagger_ui(self):
        """
            REST Api: Test Swagger UI
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "swaggerview/v1"
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 200)

    def test_class_method_permission_override(self):
        """
            REST Api: Test class method permission name override
        """

        class Model2PermOverride1(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            class_permission_name = "api"
            method_permission_name = {
                "get_list": "access",
                "get": "access",
                "put": "access",
                "post": "access",
                "delete": "access",
                "info": "access",
            }

        self.model2permoverride1 = Model2PermOverride1
        self.appbuilder.add_api(Model2PermOverride1)

        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_access", "api")
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )

        client = self.app.test_client()
        token = self.login(client, "test", "test")
        uri = "api/v1/model2permoverride1/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        uri = "api/v1/model2permoverride1/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        uri = "api/v1/model2permoverride1/1"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        # Revert test data
        insert_model2(self.appbuilder.get_session, i=0)
        self.appbuilder.get_session.delete(
            self.appbuilder.sm.find_user(username="test")
        )
        self.appbuilder.get_session.delete(self.appbuilder.sm.find_role("Test"))
        self.appbuilder.get_session.commit()

    def test_method_permission_override(self):
        """
            REST Api: Test method permission name override
        """

        class Model2PermOverride2(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            method_permission_name = {
                "get_list": "read",
                "get": "read",
                "put": "write",
                "post": "write",
                "delete": "write",
                "info": "read",
            }

        self.model2permoverride2 = Model2PermOverride2
        self.appbuilder.add_api(Model2PermOverride2)

        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_read", "Model2PermOverride2"
        )
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )

        client = self.app.test_client()
        token = self.login(client, "test", "test")
        uri = "api/v1/model2permoverride2/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        uri = "api/v1/model2permoverride2/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        uri = "api/v1/model2permoverride2/1"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 401)

        # Revert test data
        self.appbuilder.get_session.delete(
            self.appbuilder.sm.find_user(username="test")
        )
        self.appbuilder.get_session.delete(self.appbuilder.sm.find_role("Test"))
        self.appbuilder.get_session.commit()

    def test_base_permission_override(self):
        """
            REST Api: Test base perms with permission name override
        """

        class Model2PermOverride3(ModelRestApi):
            datamodel = SQLAInterface(Model2)
            method_permission_name = {
                "get_list": "read",
                "get": "read",
                "put": "write",
                "post": "write",
                "delete": "write",
                "info": "read",
            }
            base_permissions = ["can_write"]

        self.model2permoverride3 = Model2PermOverride3
        self.appbuilder.add_api(Model2PermOverride3)

        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_write", "Model2PermOverride3"
        )
        self.assertEqual(pvm.permission.name, "can_write")
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_read", "Model2PermOverride3"
        )
        self.assertEqual(pvm, None)

    def test_permission_converge_compress(self):
        """
            REST Api: Test permission name converge compress
        """

        class Model1PermConverge(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            class_permission_name = "api2"
            previous_class_permission_name = "Model1Api"
            method_permission_name = {
                "get_list": "access2",
                "get": "access2",
                "put": "access2",
                "post": "access2",
                "delete": "access2",
                "info": "access2",
            }

        self.appbuilder.add_api(Model1PermConverge)
        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_get", "Model1Api")
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )
        # Remove previous class, Hack to test code change
        for i, baseview in enumerate(self.appbuilder.baseviews):
            if baseview.__class__.__name__ == "Model1Api":
                break
        self.appbuilder.baseviews.pop(i)
        for i, baseview in enumerate(self.appbuilder.baseviews):
            if baseview.__class__.__name__ == "Model1PermOverride":
                break
        self.appbuilder.baseviews.pop(i)

        target_state_transitions = {
            "add": {
                ("Model1Api", "can_get"): {("api2", "can_access2")},
                ("Model1Api", "can_delete"): {("api2", "can_access2")},
                ("Model1Api", "can_info"): {("api2", "can_access2")},
                ("Model1Api", "can_put"): {("api2", "can_access2")},
                ("Model1Api", "can_post"): {("api2", "can_access2")},
            },
            "del_role_pvm": {
                ("Model1Api", "can_put"),
                ("Model1Api", "can_delete"),
                ("Model1Api", "can_get"),
                ("Model1Api", "can_info"),
                ("Model1Api", "can_post"),
            },
            "del_views": {"Model1Api"},
            "del_perms": set(),
        }
        state_transitions = self.appbuilder.security_converge()
        self.assertEqual(state_transitions, target_state_transitions)
        role = self.appbuilder.sm.find_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_access2", "api2")
        assert pvm in role.permissions
        self.assertEqual(len(role.permissions), 1)

        # Revert test data
        self.appbuilder.get_session.delete(
            self.appbuilder.sm.find_user(username="test")
        )
        self.appbuilder.get_session.delete(self.appbuilder.sm.find_role("Test"))
        self.appbuilder.get_session.commit()

    def test_permission_converge_expand(self):
        """
            REST Api: Test permission name converge expand
        """

        class Model1PermConverge(ModelRestApi):
            datamodel = SQLAInterface(Model1)
            class_permission_name = "Model1PermOverride"
            previous_class_permission_name = "api"
            method_permission_name = {
                "get_list": "get",
                "get": "get",
                "put": "put",
                "post": "post",
                "delete": "delete",
                "info": "info",
            }
            previous_method_permission_name = {
                "get_list": "access",
                "get": "access",
                "put": "access",
                "post": "access",
                "delete": "access",
                "info": "access",
            }

        self.appbuilder.add_api(Model1PermConverge)
        role = self.appbuilder.sm.add_role("Test")
        pvm = self.appbuilder.sm.find_permission_view_menu("can_access", "api")
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            "test", "test", "user", "test@fab.org", role, "test"
        )
        # Remove previous class, Hack to test code change
        for i, baseview in enumerate(self.appbuilder.baseviews):
            if baseview.__class__.__name__ == "Model1PermOverride":
                break
        self.appbuilder.baseviews.pop(i)

        target_state_transitions = {
            "add": {
                ("api", "can_access"): {
                    ("Model1PermOverride", "can_get"),
                    ("Model1PermOverride", "can_post"),
                    ("Model1PermOverride", "can_put"),
                    ("Model1PermOverride", "can_delete"),
                    ("Model1PermOverride", "can_info"),
                }
            },
            "del_role_pvm": {("api", "can_access")},
            "del_views": {"api"},
            "del_perms": {"can_access"},
        }
        state_transitions = self.appbuilder.security_converge()
        self.assertEqual(state_transitions, target_state_transitions)
        role = self.appbuilder.sm.find_role("Test")
        self.assertEqual(len(role.permissions), 5)
