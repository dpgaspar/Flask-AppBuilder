import logging
import os
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.const import AUTH_OAUTH
from flask_appbuilder.exceptions import OAuthProviderUnknown
import jinja2
import jwt
from tests.const import USERNAME_ADMIN, USERNAME_READONLY
from tests.fixtures.users import create_default_users

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class OAuthRegistrationRoleTestCase(unittest.TestCase):
    def setUp(self):
        # start Flask
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///"
        )
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["AUTH_TYPE"] = AUTH_OAUTH
        self.app.config["OAUTH_PROVIDERS"] = [
            {
                "name": "azure",
                "icon": "fa-windows",
                "token_key": "access_token",
                "remote_app": {
                    "client_id": "CLIENT_ID",
                    "client_secret": "SECRET",
                    "api_base_url": "https://login.microsoftonline.com/TENANT_ID/oauth2",
                    "client_kwargs": {
                        "scope": "User.Read name email profile",
                        "resource": "AZURE_APPLICATION_ID",
                    },
                    "request_token_url": None,
                    "access_token_url": "https://login.microsoftonline.com/"
                    "AZURE_APPLICATION_ID/"
                    "oauth2/token",
                    "authorize_url": "https://login.microsoftonline.com/"
                    "AZURE_APPLICATION_ID/"
                    "oauth2/authorize",
                },
            }
        ]

        # start Database
        self.db = SQLA(self.app)

    def tearDown(self):
        # Remove test user
        user_alice = self.appbuilder.sm.find_user("alice")
        if user_alice:
            self.db.session.delete(user_alice)
            self.db.session.commit()

        # stop Flask
        self.app = None

        # stop Flask-AppBuilder
        self.appbuilder = None

        # stop Database
        self.db.session.remove()
        self.db = None

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
        OAUTH: test login flow for - inactive user
        """
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)
        # validate - no users are registered
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
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was not allowed to log in
        self.assertIsNone(user)

    def test__missing_username(self):
        """
        OAUTH: test login flow for - missing credentials
        """
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # create userinfo with missing info
        userinfo_missing = self.userinfo_alice.copy()
        userinfo_missing["username"] = ""

        # attempt login
        user = sm.auth_user_oauth(userinfo_missing)

        # validate - login failure (missing username)
        self.assertIsNone(user)

        # validate - no users were created
        self.assertOnlyDefaultUsers()

    def test__unregistered(self):
        """
        OAUTH: test login flow for - unregistered user
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_oauth(self.userinfo_alice)

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
        OAUTH: test login flow for - unregistered user - no self-registration
        """
        self.app.config["AUTH_USER_REGISTRATION"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was not allowed to log in
        self.assertIsNone(user)

        # validate - no users were registered
        self.assertOnlyDefaultUsers()

    def test__unregistered__single_role(self):
        """
        OAUTH: test login flow for - unregistered user
                                   - single role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "GROUP_1": ["Admin"],
            "GROUP_2": ["User"],
        }
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was registered
        self.assertEqual(len(sm.get_all_users()), 3)

        # validate - user was given the correct roles
        self.assertIn(sm.find_role("Admin"), user.roles)
        self.assertIn(sm.find_role("User"), user.roles)
        self.assertIn(sm.find_role("Public"), user.roles)

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

    def test__unregistered__multi_role(self):
        """
        OAUTH: test login flow for - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was registered
        self.assertEqual(len(sm.get_all_users()), 3)

        # validate - user was given the correct roles
        self.assertIn(sm.find_role("Admin"), user.roles)
        self.assertIn(sm.find_role("Public"), user.roles)
        self.assertIn(sm.find_role("User"), user.roles)

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

    def test__unregistered__jmespath_role(self):
        """
        OAUTH: test login flow for - unregistered user - jmespath registration role
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was registered
        self.assertEqual(len(sm.get_all_users()), 3)

        # validate - user was given the correct roles
        self.assertListEqual(user.roles, [sm.find_role("User")])

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

    def test__registered__multi_role__no_role_sync(self):
        """
        OAUTH: test login flow for - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
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
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given no roles
        self.assertListEqual(user.roles, [])

    def test__registered__multi_role__with_role_sync(self):
        """
        OAUTH: test login flow for - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {"GROUP_1": ["Admin", "User"]}
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
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
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given the correct roles
        self.assertListEqual(user.roles, [sm.find_role("Admin"), sm.find_role("User")])

    def test__registered__jmespath_role__no_role_sync(self):
        """
        OAUTH: test login flow for - registered user - jmespath registration role - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
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
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given no roles
        self.assertListEqual(user.roles, [])

    def test__registered__jmespath_role__with_role_sync(self):
        """
        OAUTH: test login flow for - registered user - jmespath registration role - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice'], username) && 'User' || 'Public'"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm
        create_default_users(self.appbuilder.session)

        # add User role
        sm.add_role("User")

        # validate - no users are registered
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
        user = sm.auth_user_oauth(self.userinfo_alice)

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given the correct roles
        self.assertListEqual(user.roles, [sm.find_role("User")])

    def test_oauth_user_info_getter(self):
        self.appbuilder = AppBuilder(self.app, self.db.session)

        @self.appbuilder.sm.oauth_user_info_getter
        def user_info_getter(sm, provider, response):
            return {"username": "test"}

        self.assertEqual(self.appbuilder.sm.oauth_user_info, user_info_getter)
        self.assertEqual(
            self.appbuilder.sm.oauth_user_info("azure", {"claim": 1}),
            {"username": "test"},
        )

    def test_oauth_user_info_unknown_provider(self):
        self.appbuilder = AppBuilder(self.app, self.db.session)
        with self.assertRaises(OAuthProviderUnknown):
            self.appbuilder.sm.oauth_user_info("unknown", {})

    def test_oauth_user_info_azure(self):
        self.appbuilder = AppBuilder(self.app, self.db.session)
        claims = {
            "aud": "test-aud",
            "iss": "https://sts.windows.net/test/",
            "iat": 7282182129,
            "nbf": 7282182129,
            "exp": 1000000000,
            "amr": ["pwd"],
            "email": "test@gmail.com",
            "family_name": "user",
            "given_name": "test",
            "idp": "live.com",
            "name": "Test user",
            "oid": "b1a54a40-8dfa-4a6d-a2b8-f90b84d4b1df",
            "unique_name": "live.com#test@gmail.com",
            "ver": "1.0",
        }

        # Create an unsigned JWT
        unsigned_jwt = jwt.encode(claims, key=None, algorithm="none")
        user_info = self.appbuilder.sm.get_oauth_user_info(
            "azure", {"access_token": "", "id_token": unsigned_jwt}
        )
        self.assertEqual(
            user_info,
            {
                "email": "test@gmail.com",
                "first_name": "test",
                "last_name": "user",
                "role_keys": [],
                "username": "b1a54a40-8dfa-4a6d-a2b8-f90b84d4b1df",
            },
        )

    def test_oauth_user_info_azure_with_jwt_validation(self):
        self.app.config["OAUTH_PROVIDERS"] = [
            {
                "name": "azure",
                "icon": "fa-windows",
                "token_key": "access_token",
                "remote_app": {
                    "client_id": "CLIENT_ID",
                    "client_secret": "SECRET",
                    "api_base_url": "https://login.microsoftonline.com/TENANT_ID/oauth2",
                    "client_kwargs": {
                        "scope": "User.Read name email profile",
                        "resource": "AZURE_APPLICATION_ID",
                        "verify_signature": True,
                    },
                    "request_token_url": None,
                    "access_token_url": "https://login.microsoftonline.com/"
                    "AZURE_APPLICATION_ID/"
                    "oauth2/token",
                    "authorize_url": "https://login.microsoftonline.com/"
                    "AZURE_APPLICATION_ID/"
                    "oauth2/authorize",
                },
            }
        ]

        self.appbuilder = AppBuilder(self.app, self.db.session)
        claims = {
            "aud": "test-aud",
            "iss": "https://sts.windows.net/test/",
            "iat": 1696601585,
            "nbf": 1696601585,
            "exp": 7282182129,  # 100 years from now ;)
            "amr": ["pwd"],
            "email": "test@gmail.com",
            "family_name": "user",
            "given_name": "test",
            "idp": "live.com",
            "name": "Test user",
            "oid": "b1a54a40-8dfa-4a6d-a2b8-f90b84d4b1df",
            "unique_name": "live.com#test@gmail.com",
            "ver": "1.0",
        }
        from unittest.mock import MagicMock

        private_key = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALeDojEka93XZ/J8
bDGgn2MIHykafgCx2D6wTZgmmhzpRH7/k7J/WSsqG6eSFg38mGJukPCa4dcG8dCL
meajEf2g4IoaYiE55yXs0ou/tixBJI8wRY+NfCluxgIcHdKhZISVO6CkR5r7diN/
SLHPsFnDd0UiMJ5c48UsJwk8T5T7AgMBAAECgYEAqalrVB+mEi1KDud1Z9RmRzqF
BI1XnPDPSfXZZyeZJ82J5BgJxubx23RMqPnopfm4MJikK64lyZTED9hg6tgskk1X
J9pc7iyU4PQf+tx4tvElyOL4OSqGss/tQHtHz76hNOR1kxeCcJsJG+WS8P0/Kmj1
0IoYKLFlb5AHr6KqDGECQQDZ0qKIzxdmZj3gSsNldc4oOQOKJgd1QSDGCOqR9p7f
oj7nuOPRVgnztqXALhNhpZXYJq8dWmpGYFi+EC1piRUDAkEA162gPgGzUJAIyhUM
sA6Uy9v64nqBnlygVpofhdvyznSf/KUsmWQZv7gpMMXnIGAQP+rqM1gJvuRtodml
hUeSqQJAHJH4J6GiHBhE/WpQ/rnY9IWl5TTfvY1xUwhQXBzQ8dxCC/rARvDWFVVb
oD1q5V/mq5dHWL5HOjvg5+0PR8xnKQJAMOdBik3AZugB1jBnrBPiUUcT3/5/HXVL
NdfEhgmVSJLRI+wf7LfxzrLnRBPbkE+334ZYjEPOEeahpS1AhrPv4QJAHpap1I+v
8m+N5G/MppasppHLJmXhnFeQsnBX7XcdYiCqHikuBlIzoQ0Cj5xbkfgMMCVORO64
r9+EFRsxA5GNYA==
-----END PRIVATE KEY-----"""
        # Create an unsigned JWT
        unsigned_jwt = jwt.encode(
            claims, key=private_key, algorithm="RS256", headers={"kid": "1"}
        )
        self.appbuilder.sm._get_microsoft_jwks = MagicMock(
            return_value={
                "keys": [
                    {
                        "alg": "RS256",
                        "e": "AQAB",
                        "kid": "1",
                        "kty": "RSA",
                        "n": "t4OiMSRr3ddn8nxsMaCfYwgfKRp-ALHYPrBNmCaaHOlEfv-"
                        "Tsn9ZKyobp5IWDfyYYm6Q8Jrh1wbx0IuZ5qMR_aDgihpiITnnJezSi7-"
                        "2LEEkjzBFj418KW7GAhwd0qFkhJU7oKRHmvt2I39Isc-wWcN3RSIwnlz"
                        "jxSwnCTxPlPs",
                        "use": "sig",
                        "x5c": [
                            "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3g6IxJGvd12fyfGwxoJ9"
                            "jCB8pGn4Asdg+sE2YJpoc6UR+/5Oyf1krKhunkhYN/JhibpDwmuHXBvHQi5n"
                            "moxH9oOCKGmIhOecl7NKLv7YsQSSPMEWPjXwpbsYCHB3SoWSElTugpEea+3Y"
                            "jf0ixz7BZw3dFIjCeXOPFLCcJPE+U+wIDAQAB"
                        ],
                    }
                ]
            }
        )
        user_info = self.appbuilder.sm.get_oauth_user_info(
            "azure", {"access_token": "", "id_token": unsigned_jwt}
        )
        self.assertEqual(
            user_info,
            {
                "email": "test@gmail.com",
                "first_name": "test",
                "last_name": "user",
                "role_keys": [],
                "username": "b1a54a40-8dfa-4a6d-a2b8-f90b84d4b1df",
            },
        )
