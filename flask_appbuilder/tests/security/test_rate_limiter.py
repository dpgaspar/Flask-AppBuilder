import logging

import hiro
import jinja2
from flask import Flask

from flask_appbuilder import SQLA, AppBuilder, BaseView
from flask_appbuilder.tests.base import FABTestCase

from ...api import BaseApi, expose
from ...security.decorators import limit
from ..const import INVALID_LOGIN_STRING, PASSWORD_ADMIN, USERNAME_ADMIN


class LimiterTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.app.config["RATELIMIT_ENABLED"] = True
        logging.basicConfig(level=logging.ERROR)

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        class Base1Api(BaseApi):
            @limit("2 per second")
            @expose("/test1")
            def test1(self, **kwargs):
                return self.response(200, message="OK")

        class TestView(BaseView):
            @limit("1 per second")
            @expose("/test")
            def test(self):
                return self.render_template(template=self.appbuilder.base_template)

        self.appbuilder.add_api(Base1Api)
        self.appbuilder.add_view(TestView, name="testview")

    def test_default_auth_rate_limit(self):
        client = self.app.test_client()

        with hiro.Timeline().freeze():
            rv = self.browser_login(client, USERNAME_ADMIN, "wrong_password")
            data = rv.data.decode("utf-8")
            self.assertIn(INVALID_LOGIN_STRING, data)

            rv = self.browser_login(client, USERNAME_ADMIN, "wrong_password")
            data = rv.data.decode("utf-8")
            self.assertIn(INVALID_LOGIN_STRING, data)

            rv = self.browser_login(client, USERNAME_ADMIN, "wrong_password")
            self.assertEqual(rv.status_code, 429)

    def test_api_rate_decorated_limit(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "api/v1/base1api/test1"
        with hiro.Timeline().freeze():
            rv = self.auth_client_get(client, token, uri)
            self.assertEqual(rv.status_code, 200)

            rv = self.auth_client_get(client, token, uri)
            self.assertEqual(rv.status_code, 200)

            rv = self.auth_client_get(client, token, uri)
            self.assertEqual(rv.status_code, 429)

    def view_rate_decorated_limit(self):
        client = self.app.test_client()
        token = self.login(client, USERNAME_ADMIN, PASSWORD_ADMIN)
        uri = "/test"
        with hiro.Timeline().freeze():
            rv = self.auth_client_get(client, token, uri)
            self.assertEqual(rv.status_code, 200)

            rv = self.auth_client_get(client, token, uri)
            self.assertEqual(rv.status_code, 429)
