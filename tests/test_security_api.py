import json
import logging
import os
from typing import List

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.extensions import db
from flask_appbuilder.security.sqla.models import Permission, Role, User, ViewMenu
import prison
from tests.base import FABTestCase
from tests.const import PASSWORD_ADMIN, USERNAME_ADMIN
from werkzeug.security import generate_password_hash


log = logging.getLogger(__name__)


class UserAPITestCase(FABTestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_security_api")

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)
        self.create_default_users(self.appbuilder)

    def tearDown(self):
        # self.appbuilder.session.close()
        # engine = self.appbuilder.session.get_bind(mapper=None, clause=None)
        # for baseview in self.appbuilder.baseviews:
        #     if hasattr(baseview, "datamodel"):
        #         baseview.datamodel.session = None
        # engine.dispose()
        self.ctx.pop()

    def _create_test_user(
        self,
        username: str,
        password: str,
        roles: List[Role],
        email: str,
        first_name="first-name",
        last_name="last-name",
    ):
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            roles=roles,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        return user

    def test_user_info(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/_info"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_user_list(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        admin_role_id = self.appbuilder.sm.find_role("Admin").id
        readonly_role_id = self.appbuilder.sm.find_role("ReadOnly").id
        query = {"order_column": "username", "order_direction": "desc"}
        uri = f"api/v1/security/users/?q={prison.dumps(query)}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "count" in response
        self.assertEqual(response["count"], 2)
        self.assertEqual(len(response["result"]), 2)
        expected_results = [
            {
                "active": True,
                "changed_by": None,
                "created_by": None,
                "created_on": "2020-01-01T00:00:00",
                "email": "admin@fab.org",
                "first_name": "admin",
                "last_name": "user",
                "roles": [{"id": admin_role_id, "name": "Admin"}],
                "username": "testadmin",
            },
            {
                "active": True,
                "changed_by": None,
                "created_by": None,
                "created_on": "2020-01-01T00:00:00",
                "email": "readonly@fab.org",
                "first_name": "readonly",
                "last_name": "readonly",
                "roles": [{"id": readonly_role_id, "name": "ReadOnly"}],
                "username": "readonly",
            },
        ]
        self.assert_response(response["result"], expected_results)
        self.assertEqual(
            [
                "active",
                "changed_by",
                "changed_on",
                "created_by",
                "created_on",
                "email",
                "fail_login_count",
                "first_name",
                "id",
                "last_login",
                "last_name",
                "login_count",
                "roles",
                "username",
            ],
            list(response["result"][0].keys()),
        )

    def test_user_list_search_username(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        readonly_role_id = self.appbuilder.sm.find_role("ReadOnly").id
        query = {"filters": [{"col": "username", "opr": "eq", "value": "readonly"}]}
        uri = f"api/v1/security/users/?q={prison.dumps(query)}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        expected_results = [
            {
                "active": True,
                "changed_by": None,
                "changed_on": "2020-01-01T00:00:00",
                "created_by": None,
                "created_on": "2020-01-01T00:00:00",
                "email": "readonly@fab.org",
                "first_name": "readonly",
                "last_name": "readonly",
                "roles": [{"id": readonly_role_id, "name": "ReadOnly"}],
                "username": "readonly",
            }
        ]
        self.assert_response(response["result"], expected_results)
        self.assertEqual(rv.status_code, 200)
        assert "count" in response
        self.assertEqual(response["count"], 1)

    def test_user_list_search_roles(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        admin_role_id = self.appbuilder.sm.find_role("Admin").id
        query = {
            "filters": [{"col": "roles", "opr": "rel_m_m", "value": admin_role_id}]
        }
        uri = f"api/v1/security/users/?q={prison.dumps(query)}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        expected_results = [
            {
                "active": True,
                "changed_by": None,
                "changed_on": "2020-01-01T00:00:00",
                "created_by": None,
                "created_on": "2020-01-01T00:00:00",
                "email": "admin@fab.org",
                "first_name": "admin",
                "last_name": "user",
                "roles": [{"id": admin_role_id, "name": "Admin"}],
                "username": "testadmin",
            }
        ]
        self.assert_response(response["result"], expected_results)
        self.assertEqual(rv.status_code, 200)
        assert "count" in response
        self.assertEqual(response["count"], 1)

    def test_get_single_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role = Role(name="test-role")
        db.session.add(role)
        db.session.commit()
        role_id = role.id
        user = self._create_test_user(
            "test-get-single-user", "password", [role], "test-get-single-user@fab.com"
        )
        uri = f"api/v1/security/users/{user.id}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)

        assert "result" in response
        result = response["result"]
        self.assertEqual(result["username"], "test-get-single-user")
        self.assertEqual(result["first_name"], "first-name")
        self.assertEqual(result["last_name"], "last-name")
        self.assertEqual(result["email"], "test-get-single-user@fab.com")
        self.assertEqual(result["roles"], [{"id": role_id, "name": "test-role"}])

        user = db.session.query(User).filter(User.id == user.id).first()
        db.session.delete(user)
        role = db.session.query(Role).filter(Role.id == role_id).first()
        db.session.delete(role)
        db.session.commit()

    def test_get_single_not_found(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/99999999"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)
        response = json.loads(rv.data)

        assert "message" in response
        self.assertEqual(response["message"], "Not found")

    def test_create_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        role = Role(name="test-create-user-api")
        db.session.add(role)
        db.session.commit()

        uri = "api/v1/security/users/"
        create_user_payload = {
            "active": True,
            "email": "fab@test_create_user_3.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "password",
            "roles": [role.id],
            "username": "fab_usear_api_test_4",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_user_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)

        assert "id" in add_user_response
        user = (
            db.session.query(User)
            .filter(User.id == add_user_response["id"])
            .one_or_none()
        )
        self.assertEqual(user.active, create_user_payload["active"])
        self.assertEqual(user.email, create_user_payload["email"])
        self.assertEqual(user.first_name, create_user_payload["first_name"])
        self.assertEqual(user.last_name, create_user_payload["last_name"])
        self.assertEqual(user.username, create_user_payload["username"])
        self.assertEqual(len(user.roles), 1)
        self.assertEqual(user.roles[0].name, "test-create-user-api")

        user = db.session.query(User).filter(User.id == user.id).first()
        db.session.delete(user)
        db.session.delete(role)
        db.session.commit()

    def test_create_user_without_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/"
        create_user_payload = {
            "active": True,
            "email": "fab@test_create_user_1.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "password",
            "roles": [],
            "username": "fab_usear_api_test_2",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_user_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 400)

        assert "message" in add_user_response
        self.assertEqual(
            add_user_response["message"], {"roles": ["Shorter than minimum length 1."]}
        )

    def test_create_user_with_invalid_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/"
        create_user_payload = {
            "active": True,
            "email": "fab@test_create_user_1.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "password",
            "roles": [999999],
            "username": "fab_usear_api_test_2",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_user_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)

        user = self.appbuilder.sm.get_user_by_id(add_user_response["id"])

        self.assertEqual(user.active, create_user_payload["active"])
        self.assertEqual(user.email, create_user_payload["email"])
        self.assertEqual(user.first_name, create_user_payload["first_name"])
        self.assertEqual(user.last_name, create_user_payload["last_name"])
        self.assertEqual(user.username, create_user_payload["username"])
        self.assertEqual(len(user.roles), 0)

        user = db.session.query(User).filter(User.id == user.id).first()
        db.session.delete(user)
        db.session.commit()

    def test_edit_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        updated_email = "test_edit_user_new7@fab.com"

        role_1 = Role(name="test-role1")
        role_2 = Role(name="test-role2")
        role_3 = Role(name="test-role3")
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(role_3)
        db.session.commit()
        user = self._create_test_user(
            "edit-user-1", "password", [role_1], "test-edit-user1@fab.com"
        )
        user_id = user.id
        role_1_id = role_1.id
        role_2_id = role_2.id
        role_3_id = role_3.id

        uri = f"api/v1/security/users/{user.id}"
        rv = self.auth_client_put(
            client,
            token,
            uri,
            {"email": updated_email, "roles": [role_2.id, role_3.id]},
        )
        self.assertEqual(rv.status_code, 200)
        updated_user = db.session.query(User).get(user_id)
        self.assertEqual(len(updated_user.roles), 2)
        update_use_roles = sorted([role.name for role in updated_user.roles])
        self.assertEqual(update_use_roles, ["test-role2", "test-role3"])
        self.assertEqual(updated_user.email, updated_email)

        roles = (
            db.session.query(Role)
            .filter(Role.id.in_([role_1_id, role_2_id, role_3_id]))
            .all()
        )
        user = db.session.query(User).filter(User.id == user_id).first()
        db.session.delete(user)
        for r in roles:
            db.session.delete(r)
        db.session.commit()

    def test_delete_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role = Role(name="delete-user-role")

        db.session.add(role)
        db.session.commit()
        user = self._create_test_user(
            "delete-user", "password", [role], "delete-user@fab.com"
        )
        role_id = role.id
        user_id = user.id

        uri = f"api/v1/security/users/{user_id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        updated_user = self.appbuilder.sm.get_user_by_id(user_id)
        assert not updated_user

        role = db.session.query(Role).filter(Role.id == role_id).one_or_none()
        db.session.delete(role)
        db.session.commit()

    def test_delete_user_not_found(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/999999"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 404)


class RolePermissionAPITestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_ADD_SECURITY_API"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)
        self.permission_model = Permission
        self.viewmenu_model = ViewMenu
        self.role_model = Role

        self.create_default_users(self.appbuilder)

    def tearDown(self):
        self.appbuilder.session.close()
        engine = self.appbuilder.session.get_bind(mapper=None, clause=None)
        for baseview in self.appbuilder.baseviews:
            if hasattr(baseview, "datamodel"):
                baseview.datamodel.session = None
        engine.dispose()
        self.ctx.pop()

    def test_list_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        count = db.session.query(self.permission_model).count()

        uri = "api/v1/security/permissions/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        response = json.loads(rv.data)

        assert "count" and "result" in response
        self.assertEqual(response["count"], count)

    def test_get_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_get_permission_api_1"
        permission = self.appbuilder.sm.add_permission(permission_name)
        permission_id = permission.id

        uri = f"api/v1/security/permissions/{permission_id}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        response = json.loads(rv.data)

        assert "id" and "result" in response
        self.assertEqual(response["id"], permission_id)
        self.assertEqual(response["result"]["name"], permission_name)

        db.session.delete(permission)

    def test_get_invalid_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/permissions/9999999"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, {"message": "Not found"})

    def test_add_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/permissions/"
        permission_name = "super duper fab permission"

        create_permission_payload = {"name": permission_name}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        self.assertEqual(rv.status_code, 405)
        permission = self.appbuilder.sm.find_permission(permission_name)
        assert permission is None

    def test_edit_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_edit_permission_api_2"
        new_permission_name = "different_test_edit_permission_api_2"
        permission = self.appbuilder.sm.add_permission(permission_name)
        permission_id = permission.id

        uri = f"api/v1/security/permissions/{permission_id}"
        rv = self.auth_client_put(client, token, uri, {"name": new_permission_name})

        self.assertEqual(rv.status_code, 405)

        new_permission = self.appbuilder.sm.find_permission(new_permission_name)
        assert new_permission is None

        self.appbuilder.sm.del_permission(permission_name)

    def test_delete_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_delete_permission_api"
        permission = self.appbuilder.sm.add_permission(permission_name)

        uri = f"api/v1/security/permissions/{permission.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 405)

        new_permission = self.appbuilder.sm.find_permission(permission_name)
        assert new_permission is not None
        self.appbuilder.sm.del_permission(permission_name)

    def test_list_view_api(self):
        """REST Api: Test view apis"""
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        count = db.session.query(self.viewmenu_model).count()

        uri = "api/v1/security/resources/"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "count" and "result" in response
        self.assertEqual(response["count"], count)

    def test_get_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        view_name = "test_get_view_api"
        view = self.appbuilder.sm.add_view_menu(view_name)
        view_id = view.id

        uri = f"api/v1/security/resources/{view_id}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "id" and "result" in response
        self.assertEqual(response["id"], view_id)
        self.assertEqual(response["result"]["name"], view_name)

        db.session.delete(view)

    def test_get_invalid_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/resources/99999999"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, {"message": "Not found"})

    def test_add_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        view_name = "super duper fab view"
        uri = "api/v1/security/resources/"
        create_permission_payload = {"name": view_name}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        self.appbuilder.sm.del_view_menu(view_name)

    def test_add_view_without_name_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/resources/"
        create_view_payload = {}
        rv = self.auth_client_post(client, token, uri, create_view_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 422)
        assert "message" in add_permission_response
        self.assertEqual(
            {"message": {"name": ["Missing data for required field."]}},
            add_permission_response,
        )

    def test_edit_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        view_name = "test_edit_view_api"
        new_view_name = "different_test_edit_view_api"
        view_menu = self.appbuilder.sm.add_view_menu(view_name)
        view_menu_id = view_menu.id

        uri = f"api/v1/security/resources/{view_menu_id}"
        rv = self.auth_client_put(client, token, uri, {"name": new_view_name})
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            put_permission_response["result"].get("name", ""), new_view_name
        )

        new_view = self.appbuilder.sm.find_view_menu(new_view_name)
        assert new_view
        self.assertEqual(new_view.name, new_view_name)

        self.appbuilder.sm.del_view_menu(new_view_name)

    def test_delete_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        view_menu_name = "test_delete_view_api"
        view_menu = self.appbuilder.sm.add_view_menu(view_menu_name)

        uri = f"api/v1/security/resources/{view_menu.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        new_view_menu = self.appbuilder.sm.find_view_menu(view_menu_name)
        assert new_view_menu is None

    def test_list_permission_view_api(self):
        """REST Api: Test permission view apis"""
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/permissions-resources/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_get_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_get_permission_view_permission"
        view_name = "test_get_permission_view_view"
        permission_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_name, view_name
        )

        uri = f"api/v1/security/permissions-resources/{permission_view_menu.id}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        self.appbuilder.sm.del_permission_view_menu(permission_name, view_name, True)

    def test_get_invalid_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/permissions-resources/9999999"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

    def test_add_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_add_permission_3"
        view_menu_name = "test_add_view_3"

        permission = self.appbuilder.sm.add_permission(permission_name)
        view_menu = self.appbuilder.sm.add_view_menu(view_menu_name)

        uri = "api/v1/security/permissions-resources/"
        create_permission_payload = {
            "permission_id": permission.id,
            "view_menu_id": view_menu.id,
        }
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        self.appbuilder.sm.del_permission_view_menu(
            permission_name, view_menu_name, True
        )

    def test_edit_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_edit_permission_view_permission"
        view_name = "test_edit_permission_view"
        new_view_name = "test_edit_permission_view_new"
        permission_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_name, view_name
        )
        new_view_menu = self.appbuilder.sm.add_view_menu(new_view_name)

        new_view_menu_id = new_view_menu.id

        uri = f"api/v1/security/permissions-resources/{permission_view_menu.id}"
        rv = self.auth_client_put(
            client, token, uri, {"view_menu_id": new_view_menu.id}
        )
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            put_permission_response["result"].get("view_menu_id", None),
            new_view_menu_id,
        )

        self.appbuilder.sm.del_view_menu(view_name)
        self.appbuilder.sm.del_permission_view_menu(
            permission_name, new_view_name, True
        )

    def test_delete_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_delete_permission_view_permission_3"
        view_name = "test_get_permission_view_3"
        permission_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_name, view_name
        )

        uri = f"api/v1/security/permissions-resources/{permission_view_menu.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        pvm = self.appbuilder.sm.find_permission_view_menu(permission_name, view_name)
        assert pvm is None

    def test_list_role_api(self):
        """REST Api: Test role apis"""
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/roles/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_get_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_get_role_api_3"
        role = self.appbuilder.sm.add_role(role_name)
        role_id = role.id

        uri = f"api/v1/security/roles/{role_id}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "id" and "result" in response
        self.assertEqual(response["result"].get("name", ""), role_name)

        db.session.delete(role)
        db.session.commit()

    def test_create_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/roles/"
        role_name = "test_create_role_api"
        create_user_payload = {"name": role_name}
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_role_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_role_response
        self.assertEqual(create_user_payload, add_role_response["result"])

        role = db.session.query(self.role_model).filter_by(name=role_name).first()
        db.session.delete(role)
        db.session.commit()

    def test_edit_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 3
        role_name = f"test_edit_role_api_{num}"
        role_2_name = f"test_edit_role_api_{num+1}"
        permission_1_name = f"test_edit_role_permission_{num}"
        permission_2_name = f"test_edit_role_permission_{num+1}"
        view_menu_name = f"test_edit_role_view_menu_{num}"

        role = self.appbuilder.sm.add_role(role_name)

        role_id = role.id

        uri = f"api/v1/security/roles/{role_id}"
        rv = self.auth_client_put(client, token, uri, {"name": role_2_name})

        put_role_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)

        self.assertEqual(put_role_response["result"].get("name", ""), role_2_name)

        self.appbuilder.sm.del_permission_view_menu(
            permission_1_name, view_menu_name, False
        )
        self.appbuilder.sm.del_permission_view_menu(
            permission_2_name, view_menu_name, False
        )
        self.appbuilder.sm.del_permission(permission_1_name)
        self.appbuilder.sm.del_permission(permission_2_name)
        self.appbuilder.sm.del_view_menu(view_menu_name)

        role = self.appbuilder.sm.find_role(role_2_name)

        db.session.delete(role)
        db.session.commit()

    def test_add_view_menu_permissions_to_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 1
        role_name = f"test_edit_role_api_{num}"
        permission_1_name = f"test_edit_role_permission_{num}"
        permission_2_name = f"test_edit_role_permission_{num+1}"
        view_menu_name = f"test_edit_role_view_menu_{num}"

        permission_1_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_1_name, view_menu_name
        )
        permission_2_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_2_name, view_menu_name
        )
        role = self.appbuilder.sm.add_role(role_name)
        role_id = role.id
        permission_1_view_menu_id = permission_1_view_menu.id
        permission_2_view_menu_id = permission_2_view_menu.id

        uri = f"api/v1/security/roles/{role_id}/permissions"
        rv = self.auth_client_post(
            client,
            token,
            uri,
            {
                "permission_view_menu_ids": [
                    permission_1_view_menu.id,
                    permission_2_view_menu.id,
                ]
            },
        )

        post_permissions_response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "result" in post_permissions_response
        self.assertEqual(
            post_permissions_response["result"]["permission_view_menu_ids"],
            [permission_1_view_menu_id, permission_2_view_menu_id],
        )

        role = self.appbuilder.sm.find_role(role_name)

        self.assertEqual(len(role.permissions), 2)
        self.assertEqual(
            sorted([p.id for p in role.permissions]),
            [permission_1_view_menu_id, permission_2_view_menu_id],
        )

        role = self.appbuilder.sm.find_role(role_name)
        db.session.delete(role)

        self.appbuilder.sm.del_permission_view_menu(
            permission_1_name, view_menu_name, cascade=True
        )
        self.appbuilder.sm.del_permission_view_menu(
            permission_2_name, view_menu_name, cascade=True
        )

    def test_add_invalid_view_menu_permissions_to_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 1
        role_name = f"test_add_permissions_to_role_api_{num}"

        role = self.appbuilder.sm.add_role(role_name)
        role_id = role.id

        uri = f"api/v1/security/roles/{role_id}/permissions"
        rv = self.auth_client_post(client, token, uri, {})

        self.assertEqual(rv.status_code, 400)
        role = self.appbuilder.sm.find_role(role_name)
        db.session.delete(role)

    def test_add_view_menu_permissions_to_invalid_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 1
        permission_1_name = f"test_edit_role_permission_{num}"
        permission_2_name = f"test_edit_role_permission_{num+1}"
        view_menu_name = f"test_edit_role_view_menu_{num}"

        permission_1_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_1_name, view_menu_name
        )
        permission_2_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_2_name, view_menu_name
        )

        uri = f"api/v1/security/roles/{9999999}/permissions"
        rv = self.auth_client_post(
            client,
            token,
            uri,
            {
                "permission_view_menu_ids": [
                    permission_1_view_menu.id,
                    permission_2_view_menu.id,
                ]
            },
        )
        self.assertEqual(rv.status_code, 404)
        self.appbuilder.sm.del_permission_view_menu(
            permission_1_name, view_menu_name, cascade=True
        )
        self.appbuilder.sm.del_permission_view_menu(
            permission_2_name, view_menu_name, cascade=True
        )

    def test_update_role_users_valid_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_user_role"
        user_name = "test_user_test"
        test_role = self.appbuilder.sm.add_role(name=role_name)
        test_user = self.appbuilder.sm.add_user(
            username=user_name,
            first_name=user_name,
            last_name=user_name,
            email="test@t3t.com",
            role=None,
        )

        uri = f"api/v1/security/roles/{test_role.id}/users"
        payload = {"user_ids": [test_user.id]}

        response = self.auth_client_put(client, token, uri, payload)
        self.assertEqual(response.status_code, 200)

        role = self.appbuilder.sm.find_role(role_name)
        user = self.appbuilder.sm.find_user(username=user_name)

        self.assertEqual(len(user.roles), 1)
        self.assertEqual(role.user[0].id, user.id)
        self.assertEqual(user.roles[0].id, role.id)
        self.appbuilder.session.delete(role)
        self.appbuilder.session.delete(user)
        self.appbuilder.session.commit()

    def test_update_role_users_invalid_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        invalid_role_id = 9999999
        uri = f"api/v1/security/roles/{invalid_role_id}/users"

        payload = {"user_ids": [1, 2]}

        response = self.auth_client_put(client, token, uri, payload)
        self.assertEqual(response.status_code, 404)

    def test_update_role_users_invalid_payload(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_invalid_user_role"
        test_role = self.appbuilder.sm.add_role(name=role_name)

        uri = f"api/v1/security/roles/{test_role.id}/users"
        payload = {}

        response = self.auth_client_put(client, token, uri, payload)
        self.assertEqual(response.status_code, 400)

        role = self.appbuilder.sm.find_role(role_name)
        self.appbuilder.session.delete(role)
        self.appbuilder.session.commit()

    def test_update_role_users_invalid_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_invalid_user_role"
        test_role = self.appbuilder.sm.add_role(name=role_name)
        self.appbuilder.session.commit()

        invalid_user_id = 999999

        uri = f"api/v1/security/roles/{test_role.id}/users"
        payload = {"user_ids": [invalid_user_id]}

        response = self.auth_client_put(client, token, uri, payload)
        self.assertEqual(response.status_code, 404)

        role = self.appbuilder.sm.find_role(role_name)
        self.assertEqual(len(role.user), 0)

        self.appbuilder.session.delete(role)
        self.appbuilder.session.commit()

    def test_list_view_menu_permissions_of_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 1
        role_name = f"test_list_role_api_{num}"
        permission_1_name = f"test_list_role_permission_{num}"
        permission_2_name = f"test_list_role_permission_{num+1}"
        view_menu_name = f"test_list_role_view_menu_{num}"

        permission_1_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_1_name, view_menu_name
        )
        permission_2_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_2_name, view_menu_name
        )
        role = self.appbuilder.sm.add_role(role_name)
        self.appbuilder.sm.add_permission_role(role, permission_1_view_menu)
        self.appbuilder.sm.add_permission_role(role, permission_2_view_menu)

        role_id = role.id
        permission_1_view_menu_id = permission_1_view_menu.id
        permission_2_view_menu_id = permission_2_view_menu.id

        uri = f"api/v1/security/roles/{role_id}/permissions/"
        rv = self.auth_client_get(client, token, uri)

        self.assertEqual(rv.status_code, 200)

        list_permissions_response = json.loads(rv.data)

        assert "result" in list_permissions_response
        self.assertEqual(len(list_permissions_response["result"]), 2)
        self.assertEqual(
            list_permissions_response["result"],
            [
                {
                    "id": permission_1_view_menu_id,
                    "permission_name": permission_1_name,
                    "view_menu_name": view_menu_name,
                },
                {
                    "id": permission_2_view_menu_id,
                    "permission_name": permission_2_name,
                    "view_menu_name": view_menu_name,
                },
            ],
        )

        role = self.appbuilder.sm.find_role(role_name)
        db.session.delete(role)

    def test_list_view_menu_permissions_of_invalid_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = f"api/v1/security/roles/{999999}/permissions/"
        rv = self.auth_client_get(client, token, uri)

        self.assertEqual(rv.status_code, 404)

    def test_delete_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_delete_role_api"
        permission_1_name = "test_delete_role_permission"
        view_menu_name = "test_delete_role_view_menu"

        permission_1_view_menu = self.appbuilder.sm.add_permission_view_menu(
            permission_1_name, view_menu_name
        )
        role = self.appbuilder.sm.add_role(role_name, [permission_1_view_menu])

        uri = f"api/v1/security/roles/{role.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        get_role = self.appbuilder.sm.find_role(role_name)
        assert get_role is None


class UserRolePermissionDisabledTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)

    def tearDown(self):
        # self.appbuilder.session.close()
        # engine = self.appbuilder.session.get_bind(mapper=None, clause=None)
        # for baseview in self.appbuilder.baseviews:
        #     if hasattr(baseview, "datamodel"):
        #         baseview.datamodel.session = None
        # engine.dispose()
        self.ctx.pop()

    def test_user_role_permission(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/security/roles/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/security/permissions/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/security/viewmenus/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/security/permissionsviewmenus/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)


class UserCustomPasswordComplexityValidatorTestCase(FABTestCase):
    @staticmethod
    def password_validator(password):
        if len(password) < 5:
            raise PasswordComplexityValidationError

    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_ADD_SECURITY_API"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_VALIDATOR"] = self.password_validator
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.appbuilder = AppBuilder(self.app)
        self.create_default_users(self.appbuilder)

    def tearDown(self):
        # self.appbuilder.session.close()
        # engine = self.appbuilder.session.get_bind(mapper=None, clause=None)
        # for baseview in self.appbuilder.baseviews:
        #     if hasattr(baseview, "datamodel"):
        #         baseview.datamodel.session = None
        # engine.dispose()
        self.ctx.pop()

    def test_password_complexity(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/"
        create_user_payload = {
            "active": True,
            "email": "fab@usertest1.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "a",
            "roles": [1],
            "username": "password complexity test user 10",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        self.assertEqual(rv.status_code, 400)

        create_user_payload["password"] = "bigger password"
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        self.assertEqual(rv.status_code, 201)

        user = (
            db.session.query(User)
            .filter(User.username == "password complexity test user 10")
            .one_or_none()
        )
        db.session.delete(user)
        db.session.commit()


class UserDefaultPasswordComplexityValidatorTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_ADD_SECURITY_API"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)
        self.create_default_users(self.appbuilder)

    def tearDown(self):
        # self.appbuilder.session.close()
        # engine = self.appbuilder.session.get_bind(mapper=None, clause=None)
        # for baseview in self.appbuilder.baseviews:
        #     if hasattr(baseview, "datamodel"):
        #         baseview.datamodel.session = None
        # engine.dispose()
        self.ctx.pop()

    def test_password_complexity(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/security/users/"
        create_user_payload = {
            "active": True,
            "email": "fab@defalultpasswordtest.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "this is very big pasword",
            "roles": [1],
            "username": "password complexity test user",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        self.assertEqual(rv.status_code, 400)

        create_user_payload["password"] = "AB@12abcef"
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        self.assertEqual(rv.status_code, 201)

        user = (
            db.session.query(User)
            .filter(User.username == "password complexity test user")
            .one_or_none()
        )
        db.session.delete(user)
        db.session.commit()
