from unittest.mock import patch

from flask_appbuilder import ModelView
from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.models.sqla.filters import FilterEqual
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Group, User
from tests.base import BaseMVCTestCase
from tests.const import (
    INVALID_LOGIN_STRING,
    PASSWORD_ADMIN,
    PASSWORD_READONLY,
    USERNAME_ADMIN,
    USERNAME_READONLY,
)
from tests.fixtures.data_models import model1_data
from tests.sqla.models import Model1, Model2

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

    def test_sec_login_no_cache(self):
        """
        Test Security Login, no cache directives
        """
        rv = self.client.get("/login/")
        assert rv.status_code == 200
        assert (
            rv.headers.get("Cache-Control")
            == "no-store, no-cache, must-revalidate, max-age=0"
        )
        assert rv.headers["Pragma"] == "no-cache"
        assert rv.headers["Expires"] == "0"

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

    def test_login_invalid_user(self):
        """
        Test Security Login, Logout, invalid login, invalid access
        """
        self.browser_logout(self.client)
        test_username = "testuser"
        test_password = "password"
        test_user = self.create_user(
            self.appbuilder,
            test_username,
            test_password,
            "Admin",
            "user",
            "user",
            "testuser@fab.org",
        )
        # Login and list with admin
        self.browser_login(self.client, test_username, test_password)
        rv = self.client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 200)

        # Using the same session make sure the user is not allowed to access when
        # the user is deactivated
        test_user.active = False
        self.appbuilder.session.merge(test_user)
        self.appbuilder.session.commit()
        rv = self.client.get("/model1view/list/")
        self.assertEqual(rv.status_code, 302)

        self.appbuilder.session.delete(test_user)
        self.appbuilder.session.commit()

    def test_db_login_no_next_url(self):
        """
        Test Security no next URL
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client, USERNAME_ADMIN, PASSWORD_ADMIN, follow_redirects=False
        )
        assert response.location == "/"

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
        assert response.location == "/users/list/"

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
        assert response.location == "/"

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
        assert response.location == "/"

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
        assert response.location == "/"

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
        assert response.location == "/"

    def test_db_login_invalid_control_characters_next_url(self):
        """
        Test Security invalid next URL with control characters
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            PASSWORD_ADMIN,
            next_url="\u0001" + "sample.com",
            follow_redirects=False,
        )
        assert response.location == "/"

    def test_db_login_failed_keep_next_url(self):
        """
        Test Security Keeping next url after failed login attempt
        """
        self.browser_logout(self.client)
        response = self.browser_login(
            self.client,
            USERNAME_ADMIN,
            f"wrong_{PASSWORD_ADMIN}",
            next_url="/users/list/",
            follow_redirects=False,
        )
        response = self.client.post(
            response.location,
            data=dict(username=USERNAME_ADMIN, password=PASSWORD_ADMIN),
            follow_redirects=False,
        )

        assert response.location == "/users/list/"

    def test_auth_builtin_roles(self):
        """
        Test Security builtin roles readonly
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_READONLY, PASSWORD_READONLY)
        with model1_data(self.appbuilder.session, 1) as model_data:
            model_id = model_data[0].id
            # Test authorized GET
            rv = client.get("/model1view/list/")
            self.assertEqual(rv.status_code, 200)
            # Test authorized SHOW
            rv = client.get(f"/model1view/show/{model_id}")
            self.assertEqual(rv.status_code, 200)
            # Test unauthorized EDIT
            rv = client.get(f"/model1view/edit/{model_id}")
            self.assertEqual(rv.status_code, 302)
            # Test unauthorized DELETE
            rv = client.get(f"/model1view/delete/{model_id}")
            self.assertEqual(rv.status_code, 302)

    def test_sec_reset_password(self):
        """
        Test Security reset password
        """
        client = self.app.test_client()
        admin_user = self.appbuilder.sm.find_user(username=USERNAME_ADMIN)
        # Try Reset My password
        rv = client.get(
            f"/users/action/resetmypassword/{admin_user.id}", follow_redirects=True
        )
        # Werkzeug update to 0.15.X sends this action to wrong redirect
        # Old test was:
        # data = rv.data.decode("utf-8")
        # ok_(ACCESS_IS_DENIED in data)
        self.assertEqual(rv.status_code, 404)

        # Reset My password
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = client.get(
            f"/users/action/resetmypassword/{admin_user.id}", follow_redirects=True
        )
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
        rv = client.get(
            f"/users/action/resetpasswords/{admin_user.id}", follow_redirects=True
        )
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

    def test_register_user_with_role(self):
        """
        Test register user with role
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
                groups=[],
                password="password",
                conf_password="password",
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Added Row", data)
        user = (
            self.appbuilder.session.query(User)
            .filter(User.username == "from test 1-1")
            .one_or_none()
        )
        self.appbuilder.session.delete(user)
        self.appbuilder.session.commit()

    def test_register_user_with_group(self):
        """
        Test register user with group
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        group = self.create_group(self.appbuilder)

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
                roles=[],
                groups=[group.id],
                password="password",
                conf_password="password",
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Added Row", data)
        user = (
            self.appbuilder.session.query(User)
            .filter(User.username == "from test 1-1")
            .one_or_none()
        )
        self.appbuilder.session.delete(user)
        self.appbuilder.session.delete(group)
        self.appbuilder.session.commit()

    def test_register_user_missing_roles_or_groups(self):
        """
        Test register user with missing roles or groups
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # don't set roles or groups
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
                groups=[],
                password="password",
                conf_password="password",
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertNotIn("Added Row", data)
        self.assertIn("Either select a role or a group", data)
        self.browser_logout(client)

    def test_edit_user_with_role(self):
        """
        Test edit user with role
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        _tmp_user = self.create_user(
            self.appbuilder,
            "tmp_user",
            "password1",
            "",
            first_name="tmp",
            last_name="user",
            email="tmp@fab.org",
            role_names=["Admin"],
        )

        # use all required params
        rv = client.get(f"/users/edit/{_tmp_user.id}", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Edit User", data)
        rv = client.post(
            f"/users/edit/{_tmp_user.id}",
            data=dict(
                first_name=_tmp_user.first_name,
                last_name=_tmp_user.last_name,
                username=_tmp_user.username,
                email="changed@changed.org",
                roles=_tmp_user.roles[0].id,
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Changed Row", data)

        user = (
            self.appbuilder.session.query(User)
            .filter(User.username == _tmp_user.username)
            .one_or_none()
        )

        assert user.email == "changed@changed.org"
        self.appbuilder.session.delete(user)
        self.appbuilder.session.commit()

    def test_edit_user_with_group(self):
        """
        Test edit user with group
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        _tmp_user = self.create_user(
            self.appbuilder,
            "tmp_user",
            "password1",
            "",
            first_name="tmp",
            last_name="user",
            email="tmp@fab.org",
            role_names=["Admin"],
        )

        # use all required params
        rv = client.get(f"/users/edit/{_tmp_user.id}", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Edit User", data)
        rv = client.post(
            f"/users/edit/{_tmp_user.id}",
            data=dict(
                first_name=_tmp_user.first_name,
                last_name=_tmp_user.last_name,
                username=_tmp_user.username,
                email="changed@changed.org",
                roles=_tmp_user.roles[0].id,
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Changed Row", data)

        user = (
            self.appbuilder.session.query(User)
            .filter(User.username == _tmp_user.username)
            .one_or_none()
        )

        assert user.email == "changed@changed.org"
        self.appbuilder.session.delete(user)
        self.appbuilder.session.commit()

    def test_edit_user_email_validation(self):
        """
        Test edit user with email not null validation
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        read_ony_user: User = (
            self.appbuilder.session.query(User)
            .filter(User.username == USERNAME_READONLY)
            .one_or_none()
        )

        # use all required params
        rv = client.get(f"/users/edit/{read_ony_user.id}", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Edit User", data)
        rv = client.post(
            f"/users/edit/{read_ony_user.id}",
            data=dict(
                first_name=read_ony_user.first_name,
                last_name=read_ony_user.last_name,
                username=read_ony_user.username,
                email=None,
                roles=read_ony_user.roles[0].id,
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("This field is required", data)

    def test_edit_user_db_fail(self):
        """
        Test edit user with DB fail
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        read_ony_user: User = (
            self.appbuilder.session.query(User)
            .filter(User.username == USERNAME_READONLY)
            .one_or_none()
        )

        # use all required params
        rv = client.get(f"/users/edit/{read_ony_user.id}", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Edit User", data)

        with patch.object(self.appbuilder.session, "merge") as mock_merge:
            with patch.object(self.appbuilder.sm, "has_access", return_value=True) as _:
                mock_merge.side_effect = Exception("BANG!")

                rv = client.post(
                    f"/users/edit/{read_ony_user.id}",
                    data=dict(
                        first_name=read_ony_user.first_name,
                        last_name=read_ony_user.last_name,
                        username=read_ony_user.username,
                        email="changed@changed.org",
                        roles=read_ony_user.roles[0].id,
                    ),
                    follow_redirects=True,
                )

                data = rv.data.decode("utf-8")
                self.assertIn("Database Error", data)

    def test_add_group(self):
        """
        Test add group
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # use all required params
        rv = client.get("/groups/add", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Add Group", data)
        rv = client.post(
            "/groups/add",
            data=dict(
                name="group1",
                label="group1",
                description="some description",
                roles=[1],
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Added Row", data)
        group = (
            self.appbuilder.session.query(Group)
            .filter(Group.name == "group1")
            .one_or_none()
        )
        self.appbuilder.session.delete(group)
        self.appbuilder.session.commit()

    def test_add_group_unique_name(self):
        """
        Test add group unique name
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        group = self.create_group(self.appbuilder)
        self.appbuilder.session.refresh(group)
        rv = client.get("/groups/add", follow_redirects=True)
        data = rv.data.decode("utf-8")
        self.assertIn("Add Group", data)
        rv = client.post(
            "/groups/add",
            data=dict(
                name=group.name,
                label="group1",
                description="some description",
                roles=[1],
            ),
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Already exists.", data)
        self.appbuilder.session.delete(group)
        self.appbuilder.session.commit()

    def test_delete_group(self):
        """
        Test delete group
        """
        client = self.app.test_client()
        _ = self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        group = self.create_group(self.appbuilder)
        rv = client.post(
            f"/groups/delete/{group.id}",
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("Deleted Row", data)
        assert self.appbuilder.sm.find_group(name="group1") is None

    def test_delete_group_with_users(self):
        """
        Test delete group with users
        """
        client = self.app.test_client()
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        group = self.create_group(self.appbuilder)
        user = self.create_user(
            self.appbuilder,
            "test_user",
            "password",
            None,
            first_name="test",
            last_name="user",
            email="test_user@fab.org",
            group_names=["group1"],
        )
        rv = client.post(
            f"/groups/delete/{group.id}",
            follow_redirects=True,
        )
        data = rv.data.decode("utf-8")
        self.assertIn("User(s) exists in the group, cannot delete", data)
        assert self.appbuilder.sm.find_group(name="group1") is not None
        self.appbuilder.session.delete(user)
        self.appbuilder.session.delete(group)
        self.appbuilder.session.commit()
