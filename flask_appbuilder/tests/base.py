import json
import unittest

from flask_appbuilder.const import (
    API_SECURITY_PASSWORD_KEY,
    API_SECURITY_PROVIDER_KEY,
    API_SECURITY_USERNAME_KEY,
    API_SECURITY_VERSION,
)


class FABTestCase(unittest.TestCase):
    @staticmethod
    def auth_client_get(client, token, uri):
        return client.get(uri, headers={"Authorization": "Bearer {}".format(token)})

    @staticmethod
    def auth_client_delete(client, token, uri):
        return client.delete(uri, headers={"Authorization": "Bearer {}".format(token)})

    @staticmethod
    def auth_client_put(client, token, uri, json):
        return client.put(
            uri, json=json, headers={"Authorization": "Bearer {}".format(token)}
        )

    @staticmethod
    def auth_client_post(client, token, uri, json):
        return client.post(
            uri, json=json, headers={"Authorization": "Bearer {}".format(token)}
        )

    @staticmethod
    def _login(client, username, password):
        """
            Login help method
        :param client: Flask test client
        :param username: username
        :param password: password
        :return: Flask client response class
        """
        return client.post(
            "api/{}/security/login".format(API_SECURITY_VERSION),
            data=json.dumps(
                {
                    API_SECURITY_USERNAME_KEY: username,
                    API_SECURITY_PASSWORD_KEY: password,
                    API_SECURITY_PROVIDER_KEY: "db",
                }
            ),
            content_type="application/json",
        )

    def login(self, client, username, password):
        # Login with default admin
        rv = self._login(client, username, password)
        try:
            return json.loads(rv.data.decode("utf-8")).get("access_token")
        except Exception:
            return rv

    def browser_login(self, client, username, password):
        # Login with default admin
        return client.post(
            "/login/",
            data=dict(username=username, password=password),
            follow_redirects=True,
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
    ):
        role_admin = appbuilder.sm.find_role(role_name)
        appbuilder.sm.add_user(
            username, first_name, last_name, email, role_admin, password
        )
