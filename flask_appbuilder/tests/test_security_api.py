import json
import logging
import os

from flask_appbuilder import SQLA

from .base import FABTestCase
from .const import PASSWORD_ADMIN, USERNAME_ADMIN

log = logging.getLogger(__name__)


class UserAPITestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.security.sqla.models import User, Role

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["ENABLE_USER_CRUD_API"] = True
        self.db = SQLA(self.app)
        self.session = self.db.session
        self.appbuilder = AppBuilder(self.app, self.session)
        self.user_model = User
        self.role_model = Role

        # TODO: this heinous hack is to avoid using stale db session leaking from
        # RolePermissionAPITestCase
        # don't know why all baseviews in Appbuilder are attached to stale session,
        # causing error when adding a new user which reads roles from this session and
        # datamodel uses stale session to add it.
        for b in self.appbuilder.baseviews:
            if hasattr(b, "datamodel") and b.datamodel.session is not None:
                b.datamodel.session = self.db.session

    def tearDown(self):
        self.appbuilder.get_session.close()
        engine = self.db.session.get_bind(mapper=None, clause=None)
        engine.dispose()

    def test_user_list(self):
        """REST Api: Test user apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        total_users = self.appbuilder.sm.count_users()
        uri = "api/v1/user/"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "count" in response
        self.assertEqual(response["count"], total_users)
        self.assertEqual(len(response["result"]), total_users)

    def test_get_single_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        username = "test_get_single_user_1"
        first_name = "first"
        last_name = "last"
        email = "test_get_single_user@fab.com"
        password = "a"
        role_name = "get_single_user_role"

        role = self.appbuilder.sm.add_role(role_name)
        user = self.appbuilder.sm.add_user(
            username, first_name, last_name, email, role, password
        )

        uri = f"api/v1/user/{user.id}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)

        assert "result" in response
        result = response["result"]
        self.assertEqual(result["username"], username)
        self.assertEqual(result["first_name"], first_name)
        self.assertEqual(result["last_name"], last_name)
        self.assertEqual(result["email"], email)
        self.assertEqual(result["roles"], [{"id": role.id, "name": role_name}])

        user = (
            self.session.query(self.user_model)
            .filter(self.user_model.id == user.id)
            .first()
        )
        self.session.delete(user)
        role = (
            self.session.query(self.role_model)
            .filter(self.role_model.id == role.id)
            .first()
        )
        self.session.delete(role)

        self.session.commit()

    def test_get_single_invalid_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        total_users = self.appbuilder.sm.count_users()

        uri = f"api/v1/user/{total_users + 1}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)
        response = json.loads(rv.data)

        assert "message" in response
        self.assertEqual(response["message"], "Not found")

    def test_create_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_create_user_api"
        role = self.appbuilder.sm.add_role(role_name)

        uri = "api/v1/user/"
        create_user_payload = {
            "active": True,
            "email": "fab@test_create_user_1.com",
            "first_name": "fab",
            "last_name": "admin",
            "password": "password",
            "roles": [role.id],
            "username": "fab_usear_api_test_2",
        }
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_user_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)

        assert "id" in add_user_response

        user = self.appbuilder.sm.get_user_by_id(add_user_response["id"])

        self.assertEqual(user.active, create_user_payload["active"])
        self.assertEqual(user.email, create_user_payload["email"])
        self.assertEqual(user.first_name, create_user_payload["first_name"])
        self.assertEqual(user.last_name, create_user_payload["last_name"])
        self.assertEqual(user.username, create_user_payload["username"])
        self.assertEqual(len(user.roles), 1)
        self.assertEqual(user.roles[0].name, role_name)

        user = (
            self.session.query(self.user_model)
            .filter(self.user_model.id == user.id)
            .first()
        )
        self.session.delete(user)
        self.session.commit()

    def test_create_user_without_role(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/user/"
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

        uri = "api/v1/user/"
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

        user = (
            self.session.query(self.user_model)
            .filter(self.user_model.id == user.id)
            .first()
        )
        self.session.delete(user)
        self.session.commit()

    def test_edit_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        username = "edit_user_13"
        first_name = "first"
        last_name = "last"
        email = "test_edit_user13@fab.com"
        password = "a"
        role_name_1 = "edit_user_role_1"
        role_name_2 = "edit_user_role_2"
        role_name_3 = "edit_user_role_3"
        updated_email = "test_edit_user_new7@fab.com"

        role_1 = self.appbuilder.sm.add_role(role_name_1)
        role_2 = self.appbuilder.sm.add_role(role_name_2)
        role_3 = self.appbuilder.sm.add_role(role_name_3)
        user = self.appbuilder.sm.add_user(
            username, first_name, last_name, email, [role_1], password
        )

        user_id = user.id
        role_1_id = role_1.id
        role_2_id = role_2.id
        role_3_id = role_3.id

        uri = f"api/v1/user/{user_id}"
        rv = self.auth_client_put(
            client,
            token,
            uri,
            {"email": updated_email, "roles": [role_2_id, role_3_id]},
        )
        self.assertEqual(rv.status_code, 200)
        updated_user = self.appbuilder.sm.get_user_by_id(user_id)
        self.assertEqual(len(updated_user.roles), 2)
        self.assertEqual(updated_user.roles[0].name, role_name_2)
        self.assertEqual(updated_user.roles[1].name, role_name_3)
        self.assertEqual(updated_user.email, updated_email)

        roles = (
            self.session.query(self.role_model)
            .filter(self.role_model.id.in_([role_1_id, role_2_id, role_3_id]))
            .all()
        )
        user = (
            self.session.query(self.user_model)
            .filter(self.user_model.id == user_id)
            .first()
        )
        self.session.delete(user)
        for r in roles:
            self.session.delete(r)
        self.session.commit()

    def test_delete_user(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        username = "delete_user_2"
        first_name = "first"
        last_name = "last"
        email = "test_delete_user_2@fab.com"
        password = "a"
        role_name_1 = "delete_user_role_2"

        role = self.appbuilder.sm.add_role(role_name_1)
        user = self.appbuilder.sm.add_user(
            username, first_name, last_name, email, [role], password
        )
        role_id = role.id
        user_id = user.id

        uri = f"api/v1/user/{user_id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        updated_user = self.appbuilder.sm.get_user_by_id(user_id)
        assert not updated_user

        role = (
            self.session.query(self.role_model)
            .filter(self.role_model.id == role_id)
            .first()
        )
        self.session.delete(role)
        self.session.commit()


class RolePermissionAPITestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["ENABLE_USER_CRUD_API"] = True
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.appbuilder.get_session.close()
        engine = self.db.session.get_bind(mapper=None, clause=None)
        engine.dispose()

    def test_permission_api(self):
        """REST Api: Test permission apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permission/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/permission/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/permission/"
        create_permission_payload = {"name": "super duper fab permission"}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        uri = f"api/v1/permission/{add_permission_response['id']}"
        rv = self.auth_client_put(
            client, token, uri, {"name": "different permission name"}
        )
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            put_permission_response["result"].get("name", ""),
            "different permission name",
        )

        uri = f"api/v1/permission/{add_permission_response['id']}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_view_api(self):
        """REST Api: Test view apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/viewmenu/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/viewmenu/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/viewmenu/"
        create_permission_payload = {"name": "super duper fab view"}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        uri = f"api/v1/viewmenu/{add_permission_response['id']}"
        rv = self.auth_client_put(
            client, token, uri, {"name": "different permission name"}
        )
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            put_permission_response["result"].get("name", ""),
            "different permission name",
        )

        uri = f"api/v1/viewmenu/{add_permission_response['id']}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_permission_view_api(self):
        """REST Api: Test permission view apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissionviewmenu/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/permissionviewmenu/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        test_permission = self.appbuilder.sm.add_permission("test_permission")
        test_view_menu = self.appbuilder.sm.add_view_menu("test_view_menu")

        uri = "api/v1/permissionviewmenu/"
        create_permission_payload = {
            "permission_id": test_permission.id,
            "view_menu_id": test_view_menu.id,
        }
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        uri = f"api/v1/permissionviewmenu/{add_permission_response['id']}"
        rv = self.auth_client_put(client, token, uri, {"view_menu_id": "2"})
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(put_permission_response["result"].get("view_menu_id", None), 2)

        uri = f"api/v1/permissionviewmenu/{add_permission_response['id']}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        self.appbuilder.sm.del_permission("test_permission")
        self.appbuilder.sm.del_view_menu("test_view_menu")

    def test_role_api(self):
        """REST Api: Test role apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/role/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/role/1"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        uri = "api/v1/role/"
        create_user_payload = {"name": "super duper role", "permissions": [1]}
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_role_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_role_response
        self.assertEqual(create_user_payload, add_role_response["result"])

        uri = f"api/v1/role/{add_role_response['id']}"
        rv = self.auth_client_put(
            client, token, uri, {"name": "different name", "permissions": [1, 2]}
        )
        put_role_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(put_role_response["result"].get("permissions", []), [1, 2])
        self.assertEqual(put_role_response["result"].get("name", ""), "different name")

        uri = f"api/v1/role/{add_role_response['id']}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)


class UserRolePermissionDisabledTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.appbuilder.get_session.close()
        engine = self.db.session.get_bind(mapper=None, clause=None)
        engine.dispose()

    def test_user_role_permission(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/user/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/role/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/permission/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/viewmenu/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/permissionviewmenu/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)


class UserPasswordComplexityTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.exceptions import PasswordComplexityValidationError
        from flask_appbuilder.security.sqla.models import User

        def passwordValidator(password):
            if len(password) < 5:
                raise PasswordComplexityValidationError

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["ENABLE_USER_CRUD_API"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_ENABLED"] = True
        self.app.config["FAB_PASSWORD_COMPLEXITY_VALIDATOR"] = passwordValidator
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.user_model = User

        # TODO: this heinous hack is to avoid using stale db session leaking from
        # RolePermissionAPITestCase
        # don't know why all baseviews in Appbuilder are attached to stale session,
        # causing error when adding a new user which reads roles from this session and
        # datamodel uses stale session to add it.
        for b in self.appbuilder.baseviews:
            if hasattr(b, "datamodel") and b.datamodel.session is not None:
                b.datamodel.session = self.db.session

    def tearDown(self):
        self.appbuilder.get_session.close()
        engine = self.db.session.get_bind(mapper=None, clause=None)
        engine.dispose()

    def test_password_complexity(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/user/"
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

        session = self.appbuilder.get_session
        user = (
            session.query(self.user_model)
            .filter(self.user_model.username == "password complexity test user 10")
            .one_or_none()
        )
        session.delete(user)
        session.commit()
