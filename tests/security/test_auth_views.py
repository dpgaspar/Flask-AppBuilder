from types import SimpleNamespace
from unittest import TestCase

from flask import Flask, g
from flask_appbuilder.security.views import (
    AuthDBView,
    AuthLDAPView,
    AuthOAuthView,
    AuthRemoteUserView,
    AuthSAMLView,
)


class AuthViewsTestCase(TestCase):
    def test_authenticated_login_uses_safe_next_url(self):
        """Every browser authentication type handles an existing session alike."""
        app = Flask(__name__)
        appbuilder = SimpleNamespace(
            get_url_for_index="/index",
            sm=SimpleNamespace(auth_remote_user_env_var="REMOTE_USER"),
        )
        app.appbuilder = appbuilder

        view_classes = (
            AuthDBView,
            AuthLDAPView,
            AuthOAuthView,
            AuthSAMLView,
            AuthRemoteUserView,
        )
        redirects = (
            ("/users/list/", "/users/list/"),
            ("https://example.com/", "/index"),
            (None, "/index"),
        )

        for view_class in view_classes:
            view = view_class()
            view.appbuilder = appbuilder
            for next_url, expected in redirects:
                with self.subTest(view_class=view_class, next_url=next_url):
                    query_string = {"next": next_url} if next_url is not None else None
                    with app.test_request_context("/login/", query_string=query_string):
                        g.user = SimpleNamespace(is_authenticated=True)
                        response = view.login()

                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(response.location, expected)
