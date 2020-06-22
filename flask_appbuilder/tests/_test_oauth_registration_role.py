import logging
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class OAuthRegistrationRoleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = SQLA(self.app)

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_self_registration_not_enabled(self):
        self.app.config["AUTH_USER_REGISTRATION"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)

        result = self.appbuilder.sm.auth_user_oauth(userinfo={"username": "testuser"})

        self.assertIsNone(result)
        self.assertEqual(len(self.appbuilder.sm.get_all_users()), 0)

    def test_register_and_attach_static_role(self):
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)

        user = self.appbuilder.sm.auth_user_oauth(userinfo={"username": "testuser"})

        self.assertEqual(user.roles[0].name, "Public")

    def test_register_and_attach_dynamic_role(self):
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config[
            "AUTH_USER_REGISTRATION_ROLE_JMESPATH"
        ] = "contains(['alice', 'celine'], username) && 'Admin' || 'Public'"
        self.appbuilder = AppBuilder(self.app, self.db.session)

        # Role for admin
        user = self.appbuilder.sm.auth_user_oauth(
            userinfo={"username": "alice", "email": "alice@example.com"}
        )
        self.assertEqual(user.roles[0].name, "Admin")

        # Role for non-admin
        user = self.appbuilder.sm.auth_user_oauth(
            userinfo={"username": "bob", "email": "bob@example.com"}
        )
        self.assertEqual(user.roles[0].name, "Public")
