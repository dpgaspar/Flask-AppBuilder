"""Tests for SAML authentication flow."""

import os
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.const import AUTH_SAML
from flask_appbuilder.security.saml.utils import map_saml_attributes
from flask_appbuilder.utils.legacy import get_sqla_class
import jinja2
from tests.const import USERNAME_ADMIN, USERNAME_READONLY
from tests.fixtures.users import create_default_users


class SAMLUtilsTestCase(unittest.TestCase):
    """Test SAML utility functions (no app context needed)."""

    def test_map_saml_attributes_basic(self):
        """SAML: test attribute mapping - basic fields"""
        saml_attrs = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": [
                "user@example.com"
            ],
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ["John"],
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ["Doe"],
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": ["johndoe"],
        }
        mapping = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "email",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "first_name",  # noqa: E501
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "last_name",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "username",
        }
        result = map_saml_attributes(saml_attrs, mapping)
        self.assertEqual(result["email"], "user@example.com")
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")
        self.assertEqual(result["username"], "johndoe")

    def test_map_saml_attributes_role_keys(self):
        """SAML: test attribute mapping - role_keys as list"""
        saml_attrs = {"groups": ["Admin", "Users"]}
        mapping = {"groups": "role_keys"}
        result = map_saml_attributes(saml_attrs, mapping)
        self.assertEqual(result["role_keys"], ["Admin", "Users"])

    def test_map_saml_attributes_fallback_to_nameid(self):
        """SAML: test attribute mapping - fallback to NameID"""
        result = map_saml_attributes({}, {}, name_id="user@example.com")
        self.assertEqual(result["username"], "user@example.com")
        self.assertEqual(result["email"], "user@example.com")

    def test_map_saml_attributes_nameid_no_email(self):
        """SAML: test attribute mapping - NameID is not an email"""
        result = map_saml_attributes({}, {}, name_id="johndoe")
        self.assertEqual(result["username"], "johndoe")
        self.assertNotIn("email", result)

    def test_map_saml_attributes_empty(self):
        """SAML: test attribute mapping - empty attributes"""
        result = map_saml_attributes({}, {})
        self.assertEqual(result, {})

    def test_map_saml_attributes_missing_attr(self):
        """SAML: test attribute mapping - missing SAML attribute skipped"""
        saml_attrs = {"email_claim": ["user@example.com"]}
        mapping = {"email_claim": "email", "name_claim": "username"}
        result = map_saml_attributes(saml_attrs, mapping)
        self.assertEqual(result["email"], "user@example.com")
        self.assertNotIn("username", result)


class SAMLRegistrationRoleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///"
        )
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["AUTH_TYPE"] = AUTH_SAML
        self.app.config["SECRET_KEY"] = "test-secret-key"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SAML_PROVIDERS"] = [
            {
                "name": "test_idp",
                "icon": "fa-key",
                "idp": {
                    "entityId": "https://idp.example.com/",
                    "singleSignOnService": {
                        "url": "https://idp.example.com/sso",
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    },
                    "singleLogoutService": {
                        "url": "https://idp.example.com/slo",
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    },
                    "x509cert": "",
                },
                "attribute_mapping": {
                    "email": "email",
                    "givenname": "first_name",
                    "surname": "last_name",
                    "name": "username",
                    "groups": "role_keys",
                },
            }
        ]
        self.app.config["SAML_CONFIG"] = {
            "strict": False,
            "debug": True,
            "sp": {
                "entityId": "http://localhost:5000/saml/metadata/",
                "assertionConsumerService": {
                    "url": "http://localhost:5000/saml/acs/",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "singleLogoutService": {
                    "url": "http://localhost:5000/saml/slo/",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            },
        }

    def tearDown(self):
        with self.app.app_context():
            user_alice = self.appbuilder.sm.find_user("alice")
            if user_alice:
                self.appbuilder.session.delete(user_alice)
                self.appbuilder.session.commit()
        self.app = None
        self.appbuilder = None

    def assertOnlyDefaultUsers(self):
        users = self.appbuilder.sm.get_all_users()
        user_names = sorted([user.username for user in users])
        self.assertEqual(user_names, [USERNAME_READONLY, USERNAME_ADMIN])

    # ----------------
    # Userinfo Objects
    # ----------------
    userinfo_alice = {
        "username": "alice",
        "first_name": "Alice",
        "last_name": "Doe",
        "email": "alice@example.com",
        "role_keys": ["GROUP_1", "GROUP_2"],
    }

    # ----------------
    # Unit Tests
    # ----------------
    def test__inactive_user(self):
        """
        SAML: test login flow for - inactive user
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # set user inactive
            new_user.active = False

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was not allowed to log in
            self.assertIsNone(user)

    def test__missing_username(self):
        """
        SAML: test login flow for - missing credentials
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # create userinfo with missing info
            userinfo_missing = self.userinfo_alice.copy()
            userinfo_missing["username"] = ""
            userinfo_missing.pop("email", None)

            # attempt login
            user = sm.auth_user_saml(userinfo_missing)

            # validate - login failure (missing username)
            self.assertIsNone(user)

            # validate - no users were created
            self.assertOnlyDefaultUsers()

    def test__unregistered(self):
        """
        SAML: test login flow for - unregistered user
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the AUTH_USER_REGISTRATION_ROLE role
            self.assertEqual(user.roles, [sm.find_role("Public")])

            # validate - user was given the correct attributes
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.com")

    def test__unregistered__no_self_register(self):
        """
        SAML: test login flow for - unregistered user - no self-registration
        """
        self.app.config["AUTH_USER_REGISTRATION"] = False
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was not allowed to log in
            self.assertIsNone(user)

            # validate - no users were registered
            self.assertOnlyDefaultUsers()

    def test__unregistered__single_role(self):
        """
        SAML: test login flow for - unregistered user - single role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "GROUP_1": ["Admin"],
            "GROUP_2": ["User"],
        }
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertIn(sm.find_role("Admin"), user.roles)
            self.assertIn(sm.find_role("User"), user.roles)
            self.assertIn(sm.find_role("Public"), user.roles)

            # validate - user was given the correct attributes
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.com")

    def test__unregistered__multi_role(self):
        """
        SAML: test login flow for - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertIn(sm.find_role("Admin"), user.roles)
            self.assertIn(sm.find_role("Public"), user.roles)
            self.assertIn(sm.find_role("User"), user.roles)

            # validate - user was given the correct attributes
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.com")

    def test__unregistered__jmespath_role(self):
        """
        SAML: test login flow for - unregistered user - jmespath registration role
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertListEqual(user.roles, [sm.find_role("User")])

            # validate - user was given the correct attributes
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.com")

    def test__registered__multi_role__no_role_sync(self):
        """
        SAML: test login flow for - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given no roles (sync is off)
            self.assertListEqual(user.roles, [])

    def test__registered__multi_role__with_role_sync(self):
        """
        SAML: test login flow for - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given the correct roles
            self.assertSetEqual(
                set(user.roles), {sm.find_role("Admin"), sm.find_role("User")}
            )

    def test__registered__jmespath_role__no_role_sync(self):
        """
        SAML: test login flow for - registered user - jmespath role - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given no roles (sync is off)
            self.assertListEqual(user.roles, [])

    def test__registered__jmespath_role__with_role_sync(self):
        """
        SAML: test login flow for - registered user - jmespath role - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - only default users exist
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_saml(self.userinfo_alice)

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given the correct roles
            self.assertListEqual(user.roles, [sm.find_role("User")])

    def test__find_user_by_email(self):
        """
        SAML: test login flow for - existing user found by email when username differs
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # register a user with a different username
            sm.add_user(
                username="alice_old",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=sm.find_role("Public"),
            )

            # attempt login with different username but same email
            userinfo = {
                "username": "alice_new",
                "first_name": "Alice",
                "last_name": "Doe",
                "email": "alice@example.com",
            }
            user = sm.auth_user_saml(userinfo)

            # validate - found existing user by email (not created a new one)
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "alice_old")

            # validate - no extra user was created
            self.assertEqual(len(sm.get_all_users()), 3)

    def test__user_info_updated_on_login(self):
        """
        SAML: test login flow for - user info updated from SAML assertion
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # register a user with old info
            sm.add_user(
                username="alice",
                first_name="OldFirst",
                last_name="OldLast",
                email="old@example.com",
                role=sm.find_role("Public"),
            )

            # attempt login with updated info
            userinfo = {
                "username": "alice",
                "first_name": "Alice",
                "last_name": "NewLast",
                "email": "alice@example.com",
            }
            user = sm.auth_user_saml(userinfo)

            # validate - user info was updated
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "NewLast")
            self.assertEqual(user.email, "alice@example.com")

    def test__email_as_username(self):
        """
        SAML: test login flow for - email used as username when username missing
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # attempt login with only email (no username)
            userinfo = {
                "email": "emailuser@example.com",
                "first_name": "Email",
                "last_name": "User",
            }
            user = sm.auth_user_saml(userinfo)

            # validate - user was created with email as username
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "emailuser@example.com")

    def test__no_username_no_email(self):
        """
        SAML: test login flow for - no username and no email
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            # attempt login with empty userinfo
            user = sm.auth_user_saml({})

            # validate - login failure
            self.assertIsNone(user)

    def test__saml_config_properties(self):
        """
        SAML: test saml_providers and saml_config properties
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            self.assertEqual(len(sm.saml_providers), 1)
            self.assertEqual(sm.saml_providers[0]["name"], "test_idp")
            self.assertIn("sp", sm.saml_config)

    def test__login_page_single_provider_redirects(self):
        """
        SAML: test login page - single provider redirects
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)

            client = self.app.test_client()
            response = client.get("/login/")
            # With single provider, should redirect to /login/test_idp
            self.assertIn(response.status_code, [301, 302])

    def test__login_page_multiple_providers(self):
        """
        SAML: test login page - multiple providers shows selection
        """
        self.app.config["SAML_PROVIDERS"].append(
            {
                "name": "second_idp",
                "icon": "fa-key",
                "idp": {
                    "entityId": "https://idp2.example.com/",
                    "singleSignOnService": {
                        "url": "https://idp2.example.com/sso",
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    },
                    "x509cert": "",
                },
                "attribute_mapping": {},
            }
        )
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)

            client = self.app.test_client()
            response = client.get("/login/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"test_idp", response.data)
            self.assertIn(b"second_idp", response.data)

    def test__acs_without_saml_response(self):
        """
        SAML: test ACS endpoint - no SAML response redirects to login
        """
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)

            client = self.app.test_client()
            response = client.post("/saml/acs/")
            # Should redirect to login with error (no valid SAML response)
            self.assertIn(response.status_code, [301, 302])


if __name__ == "__main__":
    unittest.main()
