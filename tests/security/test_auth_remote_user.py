import unittest

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.const import AUTH_REMOTE_USER
from flask_appbuilder.utils.legacy import get_sqla_class


class AuthRemoteUserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["AUTH_TYPE"] = AUTH_REMOTE_USER
        self.app.config.from_object("tests.config_api")

    def tearDown(self):
        with self.app.app_context():
            # Remove test user
            user_alice = self.appbuilder.sm.find_user("alice")
            if user_alice:
                self.appbuilder.session.delete(user_alice)
                self.appbuilder.session.commit()

            # stop Flask
            self.app = None

            # stop Flask-AppBuilder
            self.appbuilder = None

    def test_unset_remote_user_env_var(self):
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            self.assertEqual(sm.auth_remote_user_env_var, "REMOTE_USER")

    def test_set_remote_user_env_var(self):
        with self.app.app_context():
            self.app.config["AUTH_REMOTE_USER_ENV_VAR"] = "HTTP_REMOTE_USER"
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            self.assertEqual(sm.auth_remote_user_env_var, "HTTP_REMOTE_USER")

    def test_normal_login(self):
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            # register a user
            _ = sm.add_user(
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )

            self.assertTrue(sm.auth_user_remote_user("alice"))

    def test_inactive_user_login(self):
        with self.app.app_context():
            SQLA = get_sqla_class()
            db = SQLA(self.app)
            self.appbuilder = AppBuilder(self.app, db.session)
            sm = self.appbuilder.sm

            # register a user
            alice_user = sm.add_user(
                username="alice",
                first_name="Alice",
                last_name="Doe",
                email="alice@example.com",
                role=[],
            )
            alice_user.active = False
            self.assertFalse(sm.auth_user_remote_user("alice"))
