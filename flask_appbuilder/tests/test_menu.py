import logging
import os

from flask_appbuilder import SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .base import FABTestCase
from .const import MAX_PAGE_SIZE, PASSWORD_ADMIN, USERNAME_ADMIN
from .sqla.models import Model1

log = logging.getLogger(__name__)


class FlaskTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.views import ModelView

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["FAB_API_MAX_PAGE_SIZE"] = MAX_PAGE_SIZE

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        class Model1View(ModelView):
            datamodel = SQLAInterface(Model1)

        self.appbuilder.add_view(Model1View, "Model1")

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("TEAR DOWN")

    def test_menu_access_denied(self):
        """
            REST Api: Test menu logged out access denied
        :return:
        """
        uri = "/api/v1/menu/"
        client = self.app.test_client()

        # as logged out user
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 401)

    def test_menu_api(self):
        """
            REST Api: Test menu data
        """
        uri = "/api/v1/menu/"
        client = self.app.test_client()

        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("Security", data)
        self.assertIn("Model1", data)

    def test_menu_api_limited(self):
        """
            REST Api: Test limited menu data
        """
        limited_user = "user1"
        limited_password = "user1"
        limited_role = "Limited"

        role = self.appbuilder.sm.add_role(limited_role)
        pvm = self.appbuilder.sm.find_permission_view_menu("menu_access", "Model1")
        self.appbuilder.sm.add_permission_role(role, pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu("can_get", "MenuApi")
        self.appbuilder.sm.add_permission_role(role, pvm)
        self.appbuilder.sm.add_user(
            limited_user, "user1", "user1", "user1@fab.org", role, limited_password
        )

        uri = "/api/v1/menu/"
        client = self.app.test_client()
        # as limited user
        token = self.login(client, limited_user, limited_password)
        rv = self.auth_client_get(client, token, uri)
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertNotIn("Security", data)
        self.assertIn("Model1", data)

        self.browser_logout(client)

        # Revert test data
        self.appbuilder.get_session.delete(
            self.appbuilder.sm.find_user(username=limited_user)
        )
        self.appbuilder.get_session.delete(self.appbuilder.sm.find_role(limited_role))
        self.appbuilder.get_session.commit()

    def test_menu_api_public(self):
        """
            REST Api: Test public menu data
        """
        role = self.appbuilder.sm.find_role("Public")
        pvm = self.appbuilder.sm.find_permission_view_menu("menu_access", "Model1")
        self.appbuilder.sm.add_permission_role(role, pvm)
        pvm = self.appbuilder.sm.find_permission_view_menu("can_get", "MenuApi")
        self.appbuilder.sm.add_permission_role(role, pvm)

        uri = "/api/v1/menu/"
        client = self.app.test_client()
        # as limited user
        rv = client.get(uri)
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode("utf-8")
        self.assertIn("Model1", data)

        # Revert test data
        role = self.appbuilder.sm.find_role("Public")
        role.permissions = []
        self.appbuilder.get_session.commit()
