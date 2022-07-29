import logging
import os
import unittest
from unittest.mock import Mock, patch

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.security.manager import AUTH_LDAP
import jinja2
import ldap
from mockldap import MockLdap


from ..const import USERNAME_ADMIN, USERNAME_READONLY

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class LDAPSearchTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        # start MockLdap
        self.mockldap.start()
        self.ldapobj = self.mockldap["ldap://localhost/"]

        # start Flask
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI"
        )
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["AUTH_TYPE"] = AUTH_LDAP
        self.app.config["AUTH_LDAP_SERVER"] = "ldap://localhost/"
        self.app.config["AUTH_LDAP_UID_FIELD"] = "uid"
        self.app.config["AUTH_LDAP_FIRSTNAME_FIELD"] = "givenName"
        self.app.config["AUTH_LDAP_LASTNAME_FIELD"] = "sn"
        self.app.config["AUTH_LDAP_EMAIL_FIELD"] = "email"

        # start Database
        self.db = SQLA(self.app)

    def tearDown(self):
        # Remove test user
        user_alice = self.appbuilder.sm.find_user("alice")
        if user_alice:
            self.db.session.delete(user_alice)
            self.db.session.commit()
        user_natalie = self.appbuilder.sm.find_user("natalie")
        if user_natalie:
            self.db.session.delete(user_natalie)
            self.db.session.commit()

        # stop MockLdap
        self.mockldap.stop()
        del self.ldapobj

        # stop Flask
        self.app = None

        # stop Flask-AppBuilder
        self.appbuilder = None

        # stop Database
        self.db.session.remove()
        self.db = None

    def assertOnlyDefaultUsers(self):
        users = self.appbuilder.sm.get_all_users()
        user_names = [user.username for user in users]
        self.assertEqual(user_names, [USERNAME_ADMIN, USERNAME_READONLY])

    # ----------------
    # LDAP Directory
    # ----------------
    top = ("o=test", {"o": ["test"]})
    ou_users = ("ou=users,o=test", {"ou": ["users"]})
    ou_groups = ("ou=groups,o=test", {"ou": ["groups"]})
    user_admin = (
        "uid=admin,ou=users,o=test",
        {"uid": ["admin"], "userPassword": ["admin_password"]},
    )
    user_alice = (
        "uid=alice,ou=users,o=test",
        {
            "uid": ["alice"],
            "userPassword": ["alice_password"],
            "memberOf": [b"cn=staff,ou=groups,o=test"],
            "givenName": [b"Alice"],
            "sn": [b"Doe"],
            "email": [b"alice@example.com"],
        },
    )
    user_natalie = (
        "uid=natalie,ou=users,o=test",
        {
            "uid": ["natalie"],
            "userPassword": ["natalie_password"],
            "memberOf": [
                b"cn=staff,ou=groups,o=test",
                b"cn=admin,ou=groups,o=test",
                b"cn=exec,ou=groups,o=test",
            ],
            "givenName": [b"Natalie"],
            "sn": [b"Smith"],
            "email": [b"natalie@example.com"],
        },
    )
    group_admins = (
        "cn=admins,ou=groups,o=test",
        {"cn": ["admins"], "member": [user_admin[0]]},
    )
    group_staff = (
        "cn=staff,ou=groups,o=test",
        {"cn": ["staff"], "member": [user_alice[0]]},
    )
    directory = dict(
        [
            top,
            ou_users,
            ou_groups,
            user_admin,
            user_alice,
            user_natalie,
            group_admins,
            group_staff,
        ]
    )

    # ----------------
    # LDAP Queries
    # ----------------
    call_initialize = ("initialize", tuple(["ldap://localhost/"]), {})

    call_set_option = ("set_option", tuple([ldap.OPT_REFERRALS, 0]), {})
    call_bind_admin = (
        "simple_bind_s",
        tuple(["uid=admin,ou=users,o=test", "admin_password"]),
        {},
    )
    call_bind_alice = (
        "simple_bind_s",
        tuple(["uid=alice,ou=users,o=test", "alice_password"]),
        {},
    )
    call_bind_natalie = (
        "simple_bind_s",
        tuple(["uid=natalie,ou=users,o=test", "natalie_password"]),
        {},
    )
    call_search_alice = (
        "search_s",
        tuple(["ou=users,o=test", 2, "(uid=alice)", ["givenName", "sn", "email"]]),
        {},
    )
    call_search_alice_memberof = (
        "search_s",
        tuple(
            [
                "ou=users,o=test",
                2,
                "(uid=alice)",
                ["givenName", "sn", "email", "memberOf"],
            ]
        ),
        {},
    )
    call_search_natalie_memberof = (
        "search_s",
        tuple(
            [
                "ou=users,o=test",
                2,
                "(uid=natalie)",
                ["givenName", "sn", "email", "memberOf"],
            ]
        ),
        {},
    )
    call_search_alice_filter = (
        "search_s",
        tuple(
            [
                "ou=users,o=test",
                2,
                "(&(memberOf=cn=staff,ou=groups,o=test)(uid=alice))",
                ["givenName", "sn", "email"],
            ]
        ),
        {},
    )

    # ----------------
    # Unit Tests
    # ----------------
    def test___search_ldap(self):
        """
        LDAP: test `_search_ldap` method
        """
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

        # prepare `con` object
        con = ldap.initialize("ldap://localhost/")
        sm._ldap_bind_indirect(ldap, con)

        # run `_search_ldap` method
        user_dn, user_attributes = sm._search_ldap(ldap, con, "alice")

        # validate - search returned expected data
        self.assertEqual(user_dn, self.user_alice[0])
        self.assertEqual(user_attributes["givenName"], self.user_alice[1]["givenName"])
        self.assertEqual(user_attributes["sn"], self.user_alice[1]["sn"])
        self.assertEqual(user_attributes["email"], self.user_alice[1]["email"])

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [self.call_initialize, self.call_bind_admin, self.call_search_alice],
        )

    def test___search_ldap_filter(self):
        """
        LDAP: test `_search_ldap` method (with AUTH_LDAP_SEARCH_FILTER)
        """
        # MockLdap needs non-bytes for search filters, so we patch `memberOf`
        # to a string, only for this test
        with patch.dict(
            self.directory[self.user_alice[0]],
            {
                "memberOf": [
                    i.decode() for i in self.directory[self.user_alice[0]]["memberOf"]
                ]
            },
        ):
            _mockldap = MockLdap(self.directory)
            _mockldap.start()
            _ldapobj = _mockldap["ldap://localhost/"]

            self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
            self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
            self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
            self.app.config[
                "AUTH_LDAP_SEARCH_FILTER"
            ] = "(memberOf=cn=staff,ou=groups,o=test)"
            self.appbuilder = AppBuilder(self.app, self.db.session)
            sm = self.appbuilder.sm

            # prepare `con` object
            con = ldap.initialize("ldap://localhost/")
            sm._ldap_bind_indirect(ldap, con)

            # run `_search_ldap` method
            user_dn, user_info = sm._search_ldap(ldap, con, "alice")

            # validate - search returned expected data
            self.assertEqual(user_dn, self.user_alice[0])
            self.assertEqual(user_info["givenName"], self.user_alice[1]["givenName"])
            self.assertEqual(user_info["sn"], self.user_alice[1]["sn"])
            self.assertEqual(user_info["email"], self.user_alice[1]["email"])

            # validate - expected LDAP methods were called
            self.assertEqual(
                _ldapobj.methods_called(with_args=True),
                [
                    self.call_initialize,
                    self.call_bind_admin,
                    self.call_search_alice_filter,
                ],
            )

    def test___search_ldap_with_search_referrals(self):
        """
        LDAP: test `_search_ldap` method w/returned search referrals
        """
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
            self.user_alice,
            (None, ["ldap://mycompany.com/CN=Configuration,DC=mycompany,DC=com"]),
        ]
        user_dn, user_attributes = sm._search_ldap(ldap, mock_con, "alice")

        # validate - search returned expected data
        self.assertEqual(user_dn, self.user_alice[0])
        self.assertEqual(user_attributes["givenName"], self.user_alice[1]["givenName"])
        self.assertEqual(user_attributes["sn"], self.user_alice[1]["sn"])
        self.assertEqual(user_attributes["email"], self.user_alice[1]["email"])

        mock_con.search_s.assert_called()

    def test__missing_credentials(self):
        """
        LDAP: test login flow for - missing credentials
        """
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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

        # validate - expected LDAP methods were called
        self.assertEqual(self.ldapobj.methods_called(with_args=True), [])

    def test__inactive_user(self):
        """
        LDAP: test login flow for - inactive user
        """
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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

        # validate - expected LDAP methods were called
        self.assertEqual(self.ldapobj.methods_called(with_args=True), [])

    def test__multi_group_user_mapping_to_same_role(self):
        """
        LDAP: test login flow for - user in multiple groups mapping to same role
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin"],
            "cn=admin,ou=groups,o=test": ["Admin", "User"],
            "cn=exec,ou=groups,o=test": ["Public"],
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertListEqual(
            user.roles,
            [sm.find_role("Admin"), sm.find_role("Public"), sm.find_role("User")],
        )

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Natalie")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.email, "natalie@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_natalie,
                self.call_search_natalie_memberof,
            ],
        )

    def test__direct_bind__unregistered(self):
        """
        LDAP: test login flow for - direct bind - unregistered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice,
            ],
        )

    def test__direct_bind__unregistered__no_self_register(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - no self-registration
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was not allowed to log in
        self.assertIsNone(user)

        # validate - no users were registered
        self.assertOnlyDefaultUsers()

        # validate - expected LDAP methods were called
        self.assertEqual(self.ldapobj.methods_called(with_args=True), [])

    def test__direct_bind__unregistered__no_search(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was NOT allowed to log in (because registration requires search)
        self.assertIsNone(user)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [self.call_initialize, self.call_set_option, self.call_bind_alice],
        )

    def test__direct_bind__registered(self):
        """
        LDAP: test login flow for - direct bind - registered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice,
            ],
        )

    def test__direct_bind__registered__no_search(self):
        """
        LDAP: test login flow for - direct bind - registered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in (because they are already registered)
        self.assertIsInstance(user, sm.user_model)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [self.call_initialize, self.call_set_option, self.call_bind_alice],
        )

    def test__indirect_bind__unregistered(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice,
                self.call_bind_alice,
            ],
        )

    def test__indirect_bind__unregistered__no_self_register(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - no self-registration
        """  # noqa
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was not allowed to log in
        self.assertIsNone(user)

        # validate - no users were registered
        self.assertOnlyDefaultUsers()

        # validate - expected LDAP methods were called
        self.assertEqual(self.ldapobj.methods_called(with_args=True), [])

    def test__indirect_bind__unregistered__no_search(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

        # validate - no users are registered
        self.assertOnlyDefaultUsers()

        # attempt login
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was NOT allowed to log in
        # (because indirect bind requires search)
        self.assertIsNone(user)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [self.call_initialize, self.call_set_option, self.call_bind_admin],
        )

    def test__indirect_bind__registered(self):
        """
        LDAP: test login flow for - indirect bind - registered user
        """
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice,
                self.call_bind_alice,
            ],
        )

    def test__indirect_bind__registered__no_search(self):
        """
        LDAP: test login flow for - indirect bind - registered user - no ldap search
        """
        self.app.config["AUTH_LDAP_SEARCH"] = None
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was NOT allowed to log in
        # (because indirect bind requires search)
        self.assertIsNone(user)

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [self.call_initialize, self.call_set_option, self.call_bind_admin],
        )

    def test__direct_bind__unregistered__single_role(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - single role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["User"],
            "cn=admins,ou=groups,o=test": ["Admin"],
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertListEqual(user.roles, [sm.find_role("Public"), sm.find_role("User")])

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice_memberof,
            ],
        )

    def test__direct_bind__unregistered__multi_role(self):
        """
        LDAP: test login flow for - direct bind - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertListEqual(
            user.roles,
            [sm.find_role("Admin"), sm.find_role("Public"), sm.find_role("User")],
        )

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice_memberof,
            ],
        )

    def test__direct_bind__registered__multi_role__no_role_sync(self):
        """
        LDAP: test login flow for - direct bind - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given no roles
        self.assertListEqual(user.roles, [])

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice_memberof,
            ],
        )

    def test__direct_bind__registered__multi_role__with_role_sync(self):
        """
        LDAP: test login flow for - direct bind - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_USERNAME_FORMAT"] = "uid=%s,ou=users,o=test"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given the correct roles
        self.assertListEqual(user.roles, [sm.find_role("Admin"), sm.find_role("User")])

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_alice,
                self.call_search_alice_memberof,
            ],
        )

    def test__indirect_bind__unregistered__single_role(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - single role mapping
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {"cn=staff,ou=groups,o=test": ["User"]}
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertListEqual(user.roles, [sm.find_role("Public"), sm.find_role("User")])

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice_memberof,
                self.call_bind_alice,
            ],
        )

    def test__indirect_bind__unregistered__multi_role(self):
        """
        LDAP: test login flow for - indirect bind - unregistered user - multi role mapping
        """
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        self.assertListEqual(
            user.roles,
            [sm.find_role("Admin"), sm.find_role("Public"), sm.find_role("User")],
        )

        # validate - user was given the correct attributes (read from LDAP)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "alice@example.com")

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice_memberof,
                self.call_bind_alice,
            ],
        )

    def test__indirect_bind__registered__multi_role__no_role_sync(self):
        """
        LDAP: test login flow for - indirect bind - registered user - multi role mapping - no login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = False
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given no roles
        self.assertListEqual(user.roles, [])

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice_memberof,
                self.call_bind_alice,
            ],
        )

    def test__indirect_bind__registered__multi_role__with_role_sync(self):
        """
        LDAP: test login flow for - indirect bind - registered user - multi role mapping - with login role-sync
        """  # noqa
        self.app.config["AUTH_ROLES_MAPPING"] = {
            "cn=staff,ou=groups,o=test": ["Admin", "User"]
        }
        self.app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_USER"] = "uid=admin,ou=users,o=test"
        self.app.config["AUTH_LDAP_BIND_PASSWORD"] = "admin_password"
        self.appbuilder = AppBuilder(self.app, self.db.session)
        sm = self.appbuilder.sm

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
        user = sm.auth_user_ldap("alice", "alice_password")

        # validate - user was allowed to log in
        self.assertIsInstance(user, sm.user_model)

        # validate - user was given the correct roles
        self.assertListEqual(user.roles, [sm.find_role("Admin"), sm.find_role("User")])

        # validate - expected LDAP methods were called
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [
                self.call_initialize,
                self.call_set_option,
                self.call_bind_admin,
                self.call_search_alice_memberof,
                self.call_bind_alice,
            ],
        )
