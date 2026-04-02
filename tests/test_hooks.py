import logging
import os
from unittest.mock import MagicMock
import uuid

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.sqla.models import Group, User
from flask_appbuilder.utils.legacy import get_sqla_class
from tests.base import FABTestCase
from tests.const import PASSWORD_ADMIN, USERNAME_ADMIN


log = logging.getLogger(__name__)


def _uid():
    return uuid.uuid4().hex[:8]


class UserApiHooksTestCase(FABTestCase):
    """Test that post_add and post_update hooks are called on UserApi."""

    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_security_api")

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)

        # Patch hooks on the registered UserApi view
        self.user_api = None
        for view in self.appbuilder.baseviews:
            if view.__class__.__name__ == "UserApi":
                self.user_api = view
                break
        self.assertIsNotNone(self.user_api, "UserApi view not found")
        self.user_api.post_add = MagicMock()
        self.user_api.post_update = MagicMock()
        self._created_users = []

    def tearDown(self):
        for username in self._created_users:
            user = self.appbuilder.sm.find_user(username=username)
            if user:
                self.appbuilder.session.delete(user)
        self.appbuilder.session.commit()
        self.ctx.pop()

    def test_post_add_called_on_create_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uid = _uid()
        role = self.appbuilder.sm.find_role("Admin")
        username = f"hook_add_{uid}"
        payload = {
            "active": True,
            "email": f"hook_add_{uid}@fab.com",
            "first_name": "hook",
            "last_name": "test",
            "password": "password",
            "roles": [role.id],
            "username": username,
        }
        rv = self.auth_client_post(client, token, "api/v1/security/users/", payload)
        self.assertEqual(rv.status_code, 201)
        self._created_users.append(username)
        self.user_api.post_add.assert_called_once()
        called_model = self.user_api.post_add.call_args[0][0]
        self.assertIsInstance(called_model, User)
        self.assertEqual(called_model.username, username)

    def test_post_update_called_on_edit_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uid = _uid()
        edit_username = f"hook_edit_{uid}"
        role = self.appbuilder.sm.find_role("Admin")
        user = self.appbuilder.sm.add_user(
            username=edit_username,
            first_name="hook",
            last_name="edit",
            email=f"hook_edit_{uid}@fab.com",
            role=role,
            password="password",
        )
        self._created_users.append(edit_username)

        rv = self.auth_client_put(
            client,
            token,
            f"api/v1/security/users/{user.id}",
            {"first_name": "updated_hook"},
        )
        self.assertEqual(rv.status_code, 200)
        self.user_api.post_update.assert_called_once()
        called_model = self.user_api.post_update.call_args[0][0]
        self.assertIsInstance(called_model, User)
        self.assertEqual(called_model.first_name, "updated_hook")


class GroupApiHooksTestCase(FABTestCase):
    """Test that post_add and post_update hooks are called on GroupApi."""

    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_ADD_SECURITY_API"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)

        # Patch hooks on the registered GroupApi view
        self.group_api = None
        for view in self.appbuilder.baseviews:
            if view.__class__.__name__ == "GroupApi":
                self.group_api = view
                break
        self.assertIsNotNone(self.group_api, "GroupApi view not found")
        self.group_api.post_add = MagicMock()
        self.group_api.post_update = MagicMock()

    def tearDown(self):
        groups = self.appbuilder.session.query(Group).all()
        for group in groups:
            group.users = []
            group.roles = []
            self.appbuilder.session.delete(group)
        self.appbuilder.session.commit()
        self.appbuilder.session.close()
        self.ctx.pop()

    def test_post_add_called_on_create_group(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        payload = {
            "name": "hook_test_group",
            "label": "Hook Test",
            "description": "Test group for hooks",
        }
        rv = self.auth_client_post(client, token, "api/v1/security/groups/", payload)
        self.assertEqual(rv.status_code, 201)
        self.group_api.post_add.assert_called_once()
        called_model = self.group_api.post_add.call_args[0][0]
        self.assertIsInstance(called_model, Group)
        self.assertEqual(called_model.name, "hook_test_group")

    def test_post_update_called_on_edit_group(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        group = self.appbuilder.sm.add_group("hook_edit_group", "label", "description")
        self.appbuilder.session.commit()

        rv = self.auth_client_put(
            client,
            token,
            f"api/v1/security/groups/{group.id}",
            {"label": "updated_label"},
        )
        self.assertEqual(rv.status_code, 200)
        self.group_api.post_update.assert_called_once()
        called_model = self.group_api.post_update.call_args[0][0]
        self.assertIsInstance(called_model, Group)


class AuthEventHooksTestCase(FABTestCase):
    """Test on_user_login, on_user_login_failed, and on_user_logout hooks."""

    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_security_api")

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)

        # Patch auth hooks on the security manager
        self.appbuilder.sm.on_user_login = MagicMock()
        self.appbuilder.sm.on_user_login_failed = MagicMock()
        self.appbuilder.sm.on_user_logout = MagicMock()

    def tearDown(self):
        self.ctx.pop()

    def test_on_user_login_called_on_successful_login(self):
        client = self.app.test_client()
        rv = self._login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        self.assertEqual(rv.status_code, 200)

        self.appbuilder.sm.on_user_login.assert_called_once()
        called_user = self.appbuilder.sm.on_user_login.call_args[0][0]
        self.assertEqual(called_user.username, USERNAME_ADMIN)
        self.appbuilder.sm.on_user_login_failed.assert_not_called()

    def test_on_user_login_failed_called_on_bad_password(self):
        client = self.app.test_client()
        rv = self._login(client, USERNAME_ADMIN, "wrong_password")
        self.assertEqual(rv.status_code, 401)

        self.appbuilder.sm.on_user_login_failed.assert_called_once()
        called_user = self.appbuilder.sm.on_user_login_failed.call_args[0][0]
        self.assertEqual(called_user.username, USERNAME_ADMIN)
        self.appbuilder.sm.on_user_login.assert_not_called()

    def test_on_user_logout_called_on_logout(self):
        client = self.app.test_client()
        # Login via browser (session-based) so logout works
        self.browser_login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        # Verify user is logged in by accessing a protected resource
        rv = client.get("/logout/", follow_redirects=False)
        self.assertIn(rv.status_code, (301, 302))

        self.appbuilder.sm.on_user_logout.assert_called_once()
        called_user = self.appbuilder.sm.on_user_logout.call_args[0][0]
        self.assertIsNotNone(called_user)
        self.assertEqual(called_user.username, USERNAME_ADMIN)

    def test_hooks_receive_correct_user_object(self):
        """Verify hooks receive the actual User model instance."""
        client = self.app.test_client()
        rv = self._login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        self.assertEqual(rv.status_code, 200)

        called_user = self.appbuilder.sm.on_user_login.call_args[0][0]
        self.assertIsInstance(called_user, User)
        self.assertTrue(called_user.is_authenticated)
