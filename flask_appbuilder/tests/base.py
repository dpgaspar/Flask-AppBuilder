import json
import logging
from typing import Any, Dict, List, Optional, Set
import unittest

from flask import Flask, Response
from flask.testing import FlaskClient
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.const import (
    API_SECURITY_PASSWORD_KEY,
    API_SECURITY_PROVIDER_KEY,
    API_SECURITY_REFRESH_KEY,
    API_SECURITY_USERNAME_KEY,
    API_SECURITY_VERSION,
)
import jinja2


class FABTestCase(unittest.TestCase):
    @staticmethod
    def auth_client_get(client, token, uri):
        return client.get(uri, headers={"Authorization": f"Bearer {token}"})

    @staticmethod
    def auth_client_delete(client, token, uri):
        return client.delete(uri, headers={"Authorization": f"Bearer {token}"})

    @staticmethod
    def auth_client_put(client, token, uri, json):
        return client.put(uri, json=json, headers={"Authorization": f"Bearer {token}"})

    @staticmethod
    def auth_client_post(client, token, uri, json):
        return client.post(uri, json=json, headers={"Authorization": f"Bearer {token}"})

    @staticmethod
    def _login(client, username, password, refresh: bool = False):
        """
            Login help method
        :param client: Flask test client
        :param username: username
        :param password: password
        :return: Flask client response class
        """
        return client.post(
            f"api/{API_SECURITY_VERSION}/security/login",
            json={
                API_SECURITY_USERNAME_KEY: username,
                API_SECURITY_PASSWORD_KEY: password,
                API_SECURITY_PROVIDER_KEY: "db",
                API_SECURITY_REFRESH_KEY: refresh,
            },
        )

    def login(self, client, username, password):
        rv = self._login(client, username, password)
        try:
            return json.loads(rv.data.decode("utf-8")).get("access_token")
        except Exception:
            return rv

    def browser_login(
        self,
        client: FlaskClient,
        username: str,
        password: str,
        next_url: Optional[str] = None,
        follow_redirects: bool = True,
    ) -> Response:
        login_url = "/login/"
        if next_url:
            login_url = f"{login_url}?next={next_url}"
        return client.post(
            login_url,
            data=dict(username=username, password=password),
            follow_redirects=follow_redirects,
        )

    def assert_response(
        self,
        response: List[Dict[str, Any]],
        expected_results: List[Dict[str, Any]],
        exclude_cols: Optional[List[str]] = None,
    ):
        exclude_cols = exclude_cols or []
        for idx, expected_result in enumerate(expected_results):
            for field_name, field_value in expected_result.items():
                if field_name not in exclude_cols:
                    self.assertEqual(
                        response[idx][field_name], expected_result[field_name]
                    )

    @staticmethod
    def browser_logout(client):
        return client.get("/logout/")

    def create_admin_user(self, appbuilder, username, password):
        self.create_user(appbuilder, username, password, "Admin")

    @staticmethod
    def create_user(
        appbuilder,
        username,
        password,
        role_name,
        first_name="admin",
        last_name="user",
        email="admin@fab.org",
        role_names=None,
    ):
        roles = (
            [appbuilder.sm.find_role(role_name) for role_name in role_names]
            if role_names
            else [appbuilder.sm.find_role(role_name)]
        )
        return appbuilder.sm.add_user(
            username, first_name, last_name, email, roles, password
        )


class BaseMVCTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.jinja_env.undefined = jinja2.StrictUndefined
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        logging.basicConfig(level=logging.ERROR)

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    @property
    def registered_endpoints(self) -> Set:
        return {item.endpoint for item in self.app.url_map.iter_rules()}

    def get_registered_view_endpoints(self, view_name) -> Set:
        return {
            item.endpoint
            for item in self.app.url_map.iter_rules()
            if item.endpoint.split(".")[0] == view_name
        }
