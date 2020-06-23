import logging
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder import SQLA
from flask_appbuilder.const import AUTH_PAM
from flask_appbuilder.security.sqla.models import User
from mock import patch
from pamela import PAMError

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class PAMAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["AUTH_TYPE"] = AUTH_PAM
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = SQLA(self.app)

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_handle_no_data(self):
        """
        Auth PAM: handles login request when no data is passed
        """
        self.appbuilder = AppBuilder(self.app, self.db.session)
        result = self.appbuilder.sm.auth_user_pam("", "")
        self.assertIsNone(result)

    def test_auth_pam(self):
        """
        Auth PAM: pam authentication for login
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)

        with patch("pamela.authenticate") as authenticate:
            authenticate.return_value = None
            user = self.appbuilder.sm.auth_user_pam("test_user", "test_pass")
            self.assertIsNotNone(user)
            self.assertIsInstance(user, User)
            self.assertEqual(user.roles[0].name, "Public")

    def test_user_auth_pam_failure(self):
        """
        Auth PAM: pam authentication for login with invalid details
        """
        self.app.config["AUTH_USER_REGISTRATION"] = True
        self.app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        self.appbuilder = AppBuilder(self.app, self.db.session)

        with patch("pamela.authenticate") as authenticate:
            authenticate.side_effect = PAMError()
            user = self.appbuilder.sm.auth_user_pam("test_user", "test_pass")
            self.assertIsNone(user)

    def test_auth_pam_and_registration_disabled(self):
        """
        Auth PAM: pam authentication for login and self registration not enabled
        """
        self.app.config["AUTH_USER_REGISTRATION"] = False
        self.appbuilder = AppBuilder(self.app, self.db.session)

        with patch("pamela.authenticate") as authenticate:
            authenticate.return_value = None
            user = self.appbuilder.sm.auth_user_pam("test_user_1", "test_pass_1")
            self.assertIsNone(user)
