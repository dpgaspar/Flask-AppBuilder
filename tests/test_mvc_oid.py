from unittest.mock import MagicMock

from tests.base import FABTestCase


class MVCOIDTestCase(FABTestCase):
    openid = True

    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_oid")
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)

    def test_oid_login_get(self):
        """
        OID: Test login get
        """
        self.appbuilder.sm.oid.try_login = MagicMock(return_value="Login ok")

        with self.app.test_client() as client:
            response = client.get("/login/")
        self.assertEqual(response.status_code, 200)
        for provider in self.app.config["OPENID_PROVIDERS"]:
            self.assertIn(provider["name"], response.data.decode("utf-8"))

    def test_oid_login_post(self):
        """
        OID: Test login post with a valid provider
        """
        self.appbuilder.sm.oid.try_login = MagicMock(return_value="Login ok")

        with self.app.test_client() as client:
            response = client.post("/login/", data=dict(openid="OpenStack"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b"Login ok")
        self.appbuilder.sm.oid.try_login.assert_called_with(
            "https://openstackid.org/", ask_for=["email"], ask_for_optional=[]
        )

    def test_oid_login_post_invalid_provider(self):
        """
        OID: Test login post with an invalid provider
        """
        self.appbuilder.sm.oid.try_login = MagicMock(return_value="Not Ok")

        with self.app.test_client() as client:
            response = client.post("/login/", data=dict(openid="DoesNotExist"))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "/login/")
        self.appbuilder.sm.oid.try_login.assert_not_called()
