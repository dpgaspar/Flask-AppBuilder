import json
import logging
import os

from flask_appbuilder import SQLA
from flask_appbuilder.security.sqla.models import Permission, Role, ViewMenu

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
        uri = "api/v1/users/"
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

        uri = f"api/v1/users/{user.id}"
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

        uri = "api/v1/users/99999999"
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

        uri = "api/v1/users/"
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

        uri = "api/v1/users/"
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

        uri = "api/v1/users/"
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

        uri = f"api/v1/users/{user_id}"
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

        uri = f"api/v1/users/{user_id}"
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
        self.session = self.db.session
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.permission_model = Permission
        self.viewmenu_model = ViewMenu
        self.role_model = Role

    def tearDown(self):
        self.appbuilder.get_session.close()
        engine = self.db.session.get_bind(mapper=None, clause=None)
        engine.dispose()

    def test_list_permission_api(self):
        """REST Api: Test permission apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        count = self.session.query(self.permission_model).count()

        uri = "api/v1/permissions/"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "count" and "result" in response
        self.assertEqual(response["count"], count)

    def test_get_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_get_permission_api_1"
        permission = self.appbuilder.sm.add_permission(permission_name)
        permission_id = permission.id

        uri = f"api/v1/permissions/{permission_id}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "id" and "result" in response
        self.assertEqual(response["id"], permission_id)
        self.assertEqual(response["result"]["name"], permission_name)

        self.session.delete(permission)

    def test_get_invalid_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissions/9999999"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, {"message": "Not found"})

    def test_add_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissions/"
        permission_name = "super duper fab permission"

        create_permission_payload = {"name": permission_name}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_permission_response
        self.assertEqual(create_permission_payload, add_permission_response["result"])

        permission = self.appbuilder.sm.find_permission(permission_name)
        assert permission
        self.appbuilder.sm.del_permission(permission_name)

    def test_add_permission_without_name_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissions/"
        create_permission_payload = {}
        rv = self.auth_client_post(client, token, uri, create_permission_payload)
        add_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 422)
        assert "message" in add_permission_response
        self.assertEqual(
            {"message": {"name": ["Missing data for required field."]}},
            add_permission_response,
        )

    def test_edit_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_edit_permission_api_2"
        new_permission_name = "different_test_edit_permission_api_2"
        permission = self.appbuilder.sm.add_permission(permission_name)
        permission_id = permission.id

        uri = f"api/v1/permissions/{permission_id}"
        rv = self.auth_client_put(client, token, uri, {"name": new_permission_name})
        put_permission_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            put_permission_response["result"].get("name", ""), new_permission_name
        )

        new_permission = self.appbuilder.sm.find_permission(new_permission_name)
        assert new_permission
        self.assertEqual(new_permission.name, new_permission_name)

        self.appbuilder.sm.del_permission(new_permission_name)

    def test_delete_permission_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_delete_permission_api"
        permission = self.appbuilder.sm.add_permission(permission_name)

        uri = f"api/v1/permissions/{permission.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        new_permission = self.appbuilder.sm.find_permission(permission_name)
        assert new_permission is None

    def test_list_view_api(self):
        """REST Api: Test view apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        count = self.session.query(self.viewmenu_model).count()

        uri = "api/v1/viewmenus/"
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

        uri = f"api/v1/viewmenus/{view_id}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "id" and "result" in response
        self.assertEqual(response["id"], view_id)
        self.assertEqual(response["result"]["name"], view_name)

        self.session.delete(view)

    def test_get_invalid_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/viewmenus/99999999"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, {"message": "Not found"})

    def test_add_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        view_name = "super duper fab view"
        uri = "api/v1/viewmenus/"
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

        uri = "api/v1/viewmenus/"
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

        uri = f"api/v1/viewmenus/{view_menu_id}"
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

        uri = f"api/v1/viewmenus/{view_menu.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        new_view_menu = self.appbuilder.sm.find_view_menu(view_menu_name)
        assert new_view_menu is None

    def test_list_permission_view_api(self):
        """REST Api: Test permission view apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissionsviewmenus/"
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

        uri = f"api/v1/permissionsviewmenus/{permission_view_menu.id}"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        self.appbuilder.sm.del_permission_view_menu(permission_name, view_name, True)

    def test_get_invalid_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/permissionsviewmenus/9999999"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

    def test_add_permission_view_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        permission_name = "test_add_permission_3"
        view_menu_name = "test_add_view_3"

        permission = self.appbuilder.sm.add_permission(permission_name)
        view_menu = self.appbuilder.sm.add_view_menu(view_menu_name)

        uri = "api/v1/permissionsviewmenus/"
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

        uri = f"api/v1/permissionsviewmenus/{permission_view_menu.id}"
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

        uri = f"api/v1/permissionsviewmenus/{permission_view_menu.id}"
        rv = self.auth_client_delete(client, token, uri)
        self.assertEqual(rv.status_code, 200)

        pvm = self.appbuilder.sm.find_permission_view_menu(permission_name, view_name)
        assert pvm is None

    def test_list_role_api(self):
        """REST Api: Test role apis
        """
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/roles/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)

    def test_get_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        role_name = "test_get_role_api_3"
        role = self.appbuilder.sm.add_role(role_name)
        role_id = role.id

        uri = f"api/v1/roles/{role_id}"
        rv = self.auth_client_get(client, token, uri)
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        assert "id" and "result" in response
        self.assertEqual(response["result"].get("name", ""), role_name)

        self.session.delete(role)
        self.session.commit()

    def test_create_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        uri = "api/v1/roles/"
        role_name = "test_create_role_api"
        create_user_payload = {"name": role_name}
        rv = self.auth_client_post(client, token, uri, create_user_payload)
        add_role_response = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        assert "id" and "result" in add_role_response
        self.assertEqual(create_user_payload, add_role_response["result"])

        role = self.session.query(self.role_model).filter_by(name=role_name).first()
        self.session.delete(role)
        self.session.commit()

    def test_edit_role_api(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)

        num = 3
        role_name = f"test_edit_role_api_{num}"
        role_2_name = f"test_edit_role_api_{num+1}"
        permission_1_name = f"test_edit_role_permission_{num}"
        permission_2_name = f"test_edit_role_permission_{num+1}"
        view_menu_name = f"test_edit_role_view_menu_{num}"

        # permission_1_view_menu = self.appbuilder.sm.add_permission_view_menu(
        #     permission_1_name, view_menu_name
        # )
        # permission_2_view_menu = self.appbuilder.sm.add_permission_view_menu(
        #     permission_2_name, view_menu_name
        # )
        role = self.appbuilder.sm.add_role(role_name)

        role_id = role.id
        # permission_2_view_menu_id = permission_2_view_menu.id

        uri = f"api/v1/roles/{role_id}"
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

        self.session.delete(role)
        self.session.commit()

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

        # TODO: remove this
        for b in self.appbuilder.baseviews:
            if hasattr(b, "datamodel") and b.datamodel.session is not None:
                b.datamodel.session = self.db.session

        uri = f"api/v1/roles/{role_id}/permissions"
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
            [p.id for p in role.permissions],
            [permission_1_view_menu_id, permission_2_view_menu_id],
        )

        role = self.appbuilder.sm.find_role(role_name)
        self.session.delete(role)

    def test_list_view_menu_permissions_to_role(self):
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

        uri = f"api/v1/roles/{role_id}/permissions"
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
        self.session.delete(role)

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

        uri = f"api/v1/roles/{role.id}"
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

        uri = "api/v1/users/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/roles/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/permissions/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/viewmenus/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)

        uri = "api/v1/permissionsviewmenus/"
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 404)


class UserCustomPasswordComplexityValidatorTestCase(FABTestCase):
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

        # TODO:remove this hack
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

        uri = "api/v1/users/"
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


class UserDefaultPasswordComplexityValidatorTestCase(FABTestCase):
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
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.user_model = User

        # TODO:remove this hack
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

        uri = "api/v1/users/"
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

        session = self.appbuilder.get_session
        user = (
            session.query(self.user_model)
            .filter(self.user_model.username == "password complexity test user")
            .one_or_none()
        )
        session.delete(user)
        session.commit()
