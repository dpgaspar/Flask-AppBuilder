import logging
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
import jinja2
import ldap
from mockldap import MockLdap


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class LDAPSearchTestCase(unittest.TestCase):

    top = ("o=test", {"o": ["test"]})
    example = ("ou=example,o=test", {"ou": ["example"]})
    manager = (
        "cn=manager,ou=example,o=test",
        {"cn": ["manager"], "userPassword": ["ldaptest"]},
    )
    alice = (
        "cn=alice,ou=example,o=test",
        {
            "cn": ["alice"],
            "memberOf": ["cn=group,ou=groups,o=test"],
            "userPassword": ["alicepw"],
        },
    )
    group = (
        "cn=group,ou=groups,o=test",
        {"cn": ["group"], "member": ["cn=alice,ou=example,o=test"]},
    )

    directory = dict([top, example, group, manager, alice])

    @classmethod
    def setUpClass(cls):
        # We only need to create the MockLdap instance once. The content we
        # pass in will be used for all LDAP connections.
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):

        self.mockldap.start()
        self.ldapobj = self.mockldap["ldap://localhost/"]

        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.db = SQLA(self.app)

        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["AUTH_LDAP_UID_FIELD"] = "cn"
        self.app.config["AUTH_LDAP_ALLOW_SELF_SIGNED"] = False
        self.app.config["AUTH_LDAP_USE_TLS"] = False
        self.app.config["AUTH_LDAP_SERVER"] = "ldap://localhost/"
        self.app.config["AUTH_LDAP_SEARCH"] = "ou=example,o=test"
        self.app.config["AUTH_LDAP_APPEND_DOMAIN"] = False
        self.app.config["AUTH_LDAP_FIRSTNAME_FIELD"] = None
        self.app.config["AUTH_LDAP_LASTNAME_FIELD"] = None
        self.app.config["AUTH_LDAP_EMAIL_FIELD"] = None

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj
        log.debug("TEAR DOWN")

        self.appbuilder = None
        self.app = None
        self.db = None

    def test_ldapsearch(self):
        con = ldap.initialize("ldap://localhost/")
        con.simple_bind_s("cn=manager,ou=example,o=test", "ldaptest")

        self.app.config["AUTH_LDAP_SEARCH_FILTER"] = ""
        self.appbuilder = AppBuilder(self.app, self.db.session)

        initialize_call = ("initialize", ("ldap://localhost/",), {})
        simple_bind_s_call = (
            "simple_bind_s",
            ("cn=manager,ou=example,o=test", "ldaptest"),
            {},
        )
        search_s_call = (
            "search_s",
            ("ou=example,o=test", 2, "(cn=alice)", [None, None, None]),
            {},
        )

        user = self.appbuilder.sm._search_ldap(ldap, con, "alice")
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [initialize_call, simple_bind_s_call, search_s_call],
        )
        self.assertEqual(user[0][0], self.alice[0])

    def test_ldapsearchfilter(self):
        con = ldap.initialize("ldap://localhost/")
        con.simple_bind_s("cn=manager,ou=example,o=test", "ldaptest")

        self.app.config[
            "AUTH_LDAP_SEARCH_FILTER"
        ] = "(memberOf=cn=group,ou=groups,o=test)"
        self.appbuilder = AppBuilder(self.app, self.db.session)

        initialize_call = ("initialize", ("ldap://localhost/",), {})
        simple_bind_s_call = (
            "simple_bind_s",
            ("cn=manager,ou=example,o=test", "ldaptest"),
            {},
        )
        search_s_call = (
            "search_s",
            (
                "ou=example,o=test",
                2,
                "(&(memberOf=cn=group,ou=groups,o=test)(cn=alice))",
                [None, None, None],
            ),
            {},
        )

        user = self.appbuilder.sm._search_ldap(ldap, con, "alice")
        self.assertEqual(
            self.ldapobj.methods_called(with_args=True),
            [initialize_call, simple_bind_s_call, search_s_call],
        )
        self.assertEqual(user[0][0], self.alice[0])
