from flask_appbuilder import ModelView
from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.models.sqla.filters import FilterEqual
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import User

from ..base import BaseMVCTestCase
from ..const import PASSWORD_ADMIN, PASSWORD_READONLY, USERNAME_ADMIN, USERNAME_READONLY
from ..sqla.models import Model1, Model2

INVALID_LOGIN_STRING = "Invalid login"
PASSWORD_COMPLEXITY_ERROR = (
    "Must have at least two capital letters, "
    "one special character, two digits, three lower case letters and "
    "a minimal length of 10"
)


def custom_password_validator(password: str) -> None:
    """
    A simplistic example for a password validator
    """
    if password != "password":
        raise PasswordComplexityValidationError("Password must be password")


class MVCSecurityTestCase(BaseMVCTestCase):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

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

        self.appbuilder.add_view(Model2View, "Model2")

        class Model1View(ModelView):
            datamodel = SQLAInterface(Model1)
            related_views = [Model2View]
            list_columns = ["field_string", "field_integer"]

        self.appbuilder.add_view(Model1View, "Model1", category="Model1")

    def test_sec_login(self):
        """
        Test Security Login, Logout, invalid login, invalid access
        """

        # Try to List and Redirect to Login
        rv = self.client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 302)

        # Login and list with admin
        self.browser_login(self.client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = self.client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 200)

        # Logout and and try to list
        self.browser_logout(self.client)
        rv = self.client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get("/model2view/list/")
        self.assertEqual(rv.status_code, 302)

        # Invalid Login
        rv = self.browser_login(self.client, USERNAME_ADMIN, "wrong_password")
        data = rv.data.decode("utf-8")
        self.assertIn(INVALID_LOGIN_STRING, data)

    def test_db_login_no_next_url(self):
        """
        Test Security no next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client, USERNAME_ADMIN, PASSWORD_ADMIN, follow_redirects=False
        )
        assert response.location == "http://localhost/"

    def test_db_login_valid_next_url(self):
        """
        Test Security valid partial next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="/users/list/",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/users/list/"

    def test_db_login_valid_http_scheme_url(self):
        """
        Test Security valid http scheme next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="http://localhost/path",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/path"

    def test_db_login_valid_https_scheme_url(self):
        """
        Test Security valid https scheme next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="https://localhost/path",
            follow_redirects=False,
        )
        assert response.location == "https://localhost/path"

    def test_db_login_invalid_external_next_url(self):
        """
        Test Security invalid external next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="https://google.com",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/"

    def test_db_login_invalid_scheme_next_url(self):
        """
        Test Security invalid scheme next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="ftp://sample",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/"

    def test_db_login_invalid_localhost_file_next_url(self):
        """
        Test Security invalid path to localhost file next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="file:///path",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/"

    def test_db_login_invalid_no_netloc_with_scheme_next_url(self):
        """
        Test Security invalid next URL with no netloc but with scheme
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="http:///sample.com ",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/"

    def test_db_login_invalid_control_characters_next_url(self):
        """
        Test Security invalid next URL with control characters
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url=u"\u0001" + "sample.com",
            follow_redirects=False,
        )
        assert response.location == "http://localhost/"

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
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
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

    def test_sec_reset_password_default_complexity(self):
        """
        Test Security reset password with default complexity
        """
        client = self.app.test_client()
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = True

        # Reset My password
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Reset Password Form", data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="password", conf_password="password"),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")

        self.assertIn(PASSWORD_COMPLEXITY_ERROR, data)

        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="PAssword123!", conf_password="PAssword123!"),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")

        self.assertNotIn(PASSWORD_COMPLEXITY_ERROR, data)

        # Revert changes
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = False
        _ = client.post(
            "/resetmypassword/form",
            data=dict(password="password", conf_password="password"),
            follow_redirects=True,
        )

        self.browser_logout(client)

    def test_sec_reset_password_custom_complexity(self):
        """
        Test Security reset password with custom complexity
        """
        client = self.app.test_client()
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_VALIDATOR"] = custom_password_validator

        # Reset My password
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get("/users/action/resetmypassword/1", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Reset Password Form", data)
        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="123", conf_password="123"),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")

        self.assertIn("Password must be password", data)

        rv = client.post(
            "/resetmypassword/form",
            data=dict(password="password", conf_password="password"),
            follow_redirects=True,
        )
        self.browser_logout(client)

    def test_register_user(self):
        """
        Test register user
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # use all required params
        rv = client.get("/users/add", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Add User", data)
        rv = client.post(
            "/users/add",
            data=dict(
                first_name="first",
                last_name="last",
                username="from test 1-1",
                email="test1@fromtest1.com",
                roles=[1],
                password="password",
                conf_password="password",
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Added Row", data)

        # don't set roles
        rv = client.get("/users/add", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Add User", data)
        rv = client.post(
            "/users/add",
            data=dict(
                first_name="first",
                last_name="last",
                username="from test 2-1",
                email="test2@fromtest2.com",
                roles=[],
                password="password",
                conf_password="password",
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertNotIn("Added Row", data)
        self.assertIn("This field is required", data)
        self.browser_logout(client)

        user = (
            self.db.session.query(User)
            .filter(User.username == "from test 1-1")
            .one_or_none()
        )
        self.db.session.delete(user)
        self.db.session.commit()
