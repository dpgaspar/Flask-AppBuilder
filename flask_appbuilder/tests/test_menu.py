import logging
import os

from flask_appbuilder import SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .base import FABTestCase
from .sqla.models import Model1
log = logging.getLogger(__name__)

DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "general"

LIMITED_USER = "user1"
LIMITED_USER_PASSWORD = "user1"


class FlaskTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.views import ModelView

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
        self.app.config["CSRF_ENABLED"] = False
        self.app.config["SECRET_KEY"] = "thisismyscretkey"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        logging.basicConfig(level=logging.ERROR)

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        class Model1View(ModelView):
            datamodel = SQLAInterface(Model1)

        self.appbuilder.add_view(Model1View, "Model1")
        role_admin = self.appbuilder.sm.find_role("Admin")
        self.appbuilder.sm.add_user(
            DEFAULT_ADMIN_USER,
            "admin",
            "user",
            "admin@fab.org",
            role_admin,
            DEFAULT_ADMIN_PASSWORD
        )

        role_limited = self.appbuilder.sm.add_role("LimitedUser")
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "menu_access",
            "Model1"
        )
        self.appbuilder.sm.add_permission_role(role_limited, pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu(
            "can_get",
            "MenuApi"
        )
        self.appbuilder.sm.add_permission_role(role_limited, pvm)
        self.appbuilder.sm.add_user(
            LIMITED_USER,
            "user1",
            "user1",
            "user1@fab.org",
            role_limited,
            LIMITED_USER_PASSWORD
        )

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("TEAR DOWN")

    def test_menu_api(self):
        """
            REST Api: Test menu data
        """
        uri = '/api/v1/menu/'
        client = self.app.test_client()

        # as loged out user
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 401)

        # as limited user
        token = self.login(client, LIMITED_USER, LIMITED_USER_PASSWORD)
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertNotIn("Security", data)
        self.assertIn("Model1", data)

        self.browser_logout(client)

        # as admin
        token = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn("Security", data)
        self.assertIn("Model1", data)
