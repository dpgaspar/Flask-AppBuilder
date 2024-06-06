import logging
import os
from typing import List
import unittest
from unittest.mock import Mock

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.manager import AUTH_LDAP
from flask_appbuilder.security.sqla.models import User
import jinja2
import ldap
from tests.const import USERNAME_ADMIN, USERNAME_READONLY
from tests.fixtures.users import create_default_users

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class LDAPSearchTestCase(unittest.TestCase):
    def setUp(self):
        # start MockLdap
        # start Flask
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///"
        )
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["AUTH_TYPE"] = AUTH_LDAP
        self.app.config["AUTH_LDAP_SERVER"] = "ldap://localhost:1389/"
        self.app.config["AUTH_LDAP_UID_FIELD"] = "uid"
        self.app.config["AUTH_LDAP_FIRSTNAME_FIELD"] = "givenName"
        self.app.config["AUTH_LDAP_LASTNAME_FIELD"] = "sn"
        self.app.config["AUTH_LDAP_EMAIL_FIELD"] = "mail"

    def tearDown(self):
        from flask_appbuilder.extensions import db

        # Remove test user
        with self.app.app_context():
            # Remove test user
            user_alice = self.appbuilder.sm.find_user("alice")
            if user_alice:
                db.session.delete(user_alice)
                db.session.commit()
            user_natalie = self.appbuilder.sm.find_user("natalie")
            if user_natalie:
                db.session.delete(user_natalie)
                db.session.commit()

    def assertOnlyDefaultUsers(self):
        users = self.appbuilder.sm.get_all_users()
        user_names = sorted([user.username for user in users])
        self.assertEqual(user_names, [USERNAME_READONLY, USERNAME_ADMIN])

    def assertUserContainsRoles(self, user: User, role_names: List[str]):
        user_role_names = sorted([role.name for role in user.roles])
        self.assertListEqual(user_role_names, sorted(role_names))

    # ----------------
    # Unit Tests
    # ----------------
    def test___search_ldap(self):
        """
        LDAP: test `_search_ldap` method
        """
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # prepare `con` object
            con = ldap.initialize("ldap://localhost:1389/")
            sm._ldap_bind_indirect(ldap, con)

            # run `_search_ldap` method
            user_dn, user_attributes = sm._search_ldap(ldap, con, "alice")

            # validate - search returned expected data
            self.assertEqual(user_dn, "cn=alice,ou=users,dc=example,dc=org")
            self.assertEqual(user_attributes["givenName"], [b"Alice"])
            self.assertEqual(user_attributes["sn"], [b"Doe"])
            self.assertEqual(user_attributes["mail"], [b"alice@example.org"])

    def test___search_ldap_filter(self):
        """
        LDAP: test `_search_ldap` method (with AUTH_LDAP_SEARCH_FILTER)
        """
        # MockLdap needs non-bytes for search filters, so we patch `memberOf`
        # to a string, only for this test

        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_SEARCH_FILTER"
        ] = "(memberOf=cn=staff,ou=groups,dc=example,dc=org)"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # prepare `con` object
            con = ldap.initialize("ldap://localhost:1389/")
            sm._ldap_bind_indirect(ldap, con)

            # run `_search_ldap` method
            user_dn, user_attributes = sm._search_ldap(ldap, con, "alice")

            # validate - search returned expected data
            self.assertEqual(user_dn, "cn=alice,ou=users,dc=example,dc=org")
            self.assertEqual(user_attributes["givenName"], [b"Alice"])
            self.assertEqual(user_attributes["sn"], [b"Doe"])
            self.assertEqual(user_attributes["mail"], [b"alice@example.org"])

    def test___search_ldap_with_search_referrals(self):
        """
        LDAP: test `_search_ldap` method w/returned search referrals
        """
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            user_alice = (
                "cn=alice,ou=users,dc=example,dc=org",
                {
                    "uid": ["alice"],
                    "userPassword": ["alice_password"],
                    "memberOf": [b"cn=staff,ou=groups,o=test"],
                    "givenName": [b"Alice"],
                    "sn": [b"Doe"],
                    "mail": [b"alice@example.org"],
                },
            )
            # run `_search_ldap` method w/mocked ldap connection
            mock_con = Mock()
            mock_con.search_s.return_value = [
                (
                    None,
                    [
                        "ldap://ForestDnsZones.mycompany.com/"
                        "DC=ForestDnsZones,DC=mycompany,DC=com"
                    ],
                ),
                user_alice,
                (None, ["ldap://mycompany.com/CN=Configuration,DC=mycompany,DC=com"]),
            ]
            user_dn, user_attributes = sm._search_ldap(ldap, mock_con, "alice")

            # validate - search returned expected data
            self.assertEqual(user_dn, user_alice[0])
            self.assertEqual(user_attributes["givenName"], user_alice[1]["givenName"])
            self.assertEqual(user_attributes["sn"], user_alice[1]["sn"])
            self.assertEqual(user_attributes["mail"], user_alice[1]["mail"])

            mock_con.search_s.assert_called()

    def test__missing_credentials(self):
        """
        LDAP: test login flow for - missing credentials
        """
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # validate - login failure (missing username)
            self.assertIsNone(sm.auth_user_ldap(None, "password"))
            self.assertIsNone(sm.auth_user_ldap("", "password"))

            # validate - login failure (missing password)
            self.assertIsNone(sm.auth_user_ldap("username", None))
            self.assertIsNone(sm.auth_user_ldap("username", ""))

            # validate - login failure (missing username/password)
            self.assertIsNone(sm.auth_user_ldap(None, None))
            self.assertIsNone(sm.auth_user_ldap("", None))
            self.assertIsNone(sm.auth_user_ldap("", ""))
            self.assertIsNone(sm.auth_user_ldap(None, ""))

            # validate - no users were created
            self.assertOnlyDefaultUsers()

    def test__active_user(self):
        """
        LDAP: test login flow for - active user
        """
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
            new_user.active = True

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was not allowed to log in
            self.assertIsNotNone(user)

    def test__inactive_user(self):
        """
        LDAP: test login flow for - inactive user
        """
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was not allowed to log in
            self.assertIsNone(user)

    def test__multi_group_user_mapping_to_same_role(self):
        """
        LDAP: test login flow for - user in multiple groups mapping to same role
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin"],
            "cn=readers,ou=groups,dc=example,dc=org": ["User"],
        }
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("natalie", "natalie_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["Public", "User"])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Natalie")
            self.assertEqual(user.last_name, "Smith")
            self.assertEqual(user.email, "natalie@example.org")

    def test__direct_bind__unregistered(self):
        """
        LDAP: test login flow for - direct bind - unregistered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the AUTH_USER_REGISTRATION_ROLE role
            self.assertEqual(user.roles, [sm.find_role("Public")])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__direct_bind__unregistered__no_self_register(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - no self-registration
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = False
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was not allowed to log in
            self.assertIsNone(user)

            # validate - no users were registered
            self.assertOnlyDefaultUsers()

    def test__direct_bind__unregistered__no_search(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was NOT allowed to log in
            # (because registration requires search)
            self.assertIsNone(user)

    def test__direct_bind__registered(self):
        """
        LDAP: test login flow for - direct bind - registered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

    def test__direct_bind__registered__no_search(self):
        """
        LDAP: test login flow for - direct bind - registered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in (because they are already registered)
            self.assertIsInstance(user, sm.user_model)

    def test__indirect_bind__unregistered(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the AUTH_USER_REGISTRATION_ROLE role
            self.assertListEqual(user.roles, [sm.find_role("Public")])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__indirect_bind__unregistered__no_self_register(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - no self-registration
        """  # noqa
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = False
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was not allowed to log in
            self.assertIsNone(user)

            # validate - no users were registered
            self.assertOnlyDefaultUsers()

    def test__indirect_bind__unregistered__no_search(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was NOT allowed to log in
            # (because indirect bind requires search)
            self.assertIsNone(user)

    def test__indirect_bind__registered(self):
        """
        LDAP: test login flow for - indirect bind - registered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

    def test__indirect_bind__registered__no_search(self):
        """
        LDAP: test login flow for - indirect bind - registered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # register a user
            new_user = sm.add_user(  # noqa
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was NOT allowed to log in
            # (because indirect bind requires search)
            self.assertIsNone(user)

    def test__direct_bind__unregistered__single_role(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - single role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["Admin", "Public"])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__direct_bind__unregistered__multi_role(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["Admin", "Public", "User"])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__direct_bind__registered__multi_role__no_role_sync(self):
        """
        LDAP: test login flow for - direct bind - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given no roles
            self.assertListEqual(user.roles, [])

    def test__direct_bind__registered__multi_role__with_role_sync(self):
        """
        LDAP: test login flow for - direct bind - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["Admin", "User"])

    def test__indirect_bind__unregistered__single_role(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - single role mapping
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["User"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["Public", "User"])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__indirect_bind__unregistered__multi_role(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            sm = self.appbuilder.sm
            create_default_users(self.appbuilder.session)

            # add User role
            sm.add_role("User")

            # validate - no users are registered
            self.assertOnlyDefaultUsers()

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["User", "Public", "Admin"])

            # validate - user was given the correct attributes (read from LDAP)
            self.assertEqual(user.first_name, "Alice")
            self.assertEqual(user.last_name, "Doe")
            self.assertEqual(user.email, "alice@example.org")

    def test__indirect_bind__registered__multi_role__no_role_sync(self):
        """
        LDAP: test login flow for - indirect bind - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given no roles
            self.assertListEqual(user.roles, [])

    def test__indirect_bind__registered__multi_role__with_role_sync(self):
        """
        LDAP: test login flow for - indirect bind - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,dc=example,dc=org": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_USER"] = "cn=admin,dc=example,dc=org"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
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
                email="alice@example.org",
                role=[],
            )

            # validate - user was registered
            self.assertEqual(len(sm.get_all_users()), 3)

            # attempt login
            user = sm.auth_user_ldap("alice", "alice_password")

            # validate - user was allowed to log in
            self.assertIsInstance(user, sm.user_model)

            # validate - user was given the correct roles
            self.assertUserContainsRoles(user, ["User", "Admin"])

    def test_login_failed_keep_next_url(self):
        """
        LDAP: Keeping next url after failed login attempt
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=example,dc=org"
        self.app.config[
            "AUTH_LDAP_USERNAME_FORMAT"
        ] = "cn=%s,ou=users,dc=example,dc=org"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SECRET_KEY"] = "thisismyscretkey"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            client = self.app.test_client()
            client.get("/logout/")

            response = client.post(
                "/login/?next=/users/userinfo/",
                data=dict(username="natalie", password="wrong_natalie_password"),
                follow_redirects=False,
            )
            response = client.post(
                response.location,
                data=dict(username="natalie", password="natalie_password"),
                follow_redirects=False,
            )
            assert response.location == "/users/userinfo/"
