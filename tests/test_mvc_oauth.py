from urllib.parse import quote

from flask_appbuilder.extensions import db
from flask_appbuilder.security.sqla.models import User
from flask_login import current_user
import jwt
from tests.base import FABTestCase


class UserInfoReponseMock:
    def json(self):
        return {
            "id": "1",
            "given_name": "first-name",
            "family_name": "last-name",
            "email": "user1@fab.org",
        }


class OAuthRemoteMock:
    def authorize_access_token(self):
        return {"access_token": "some-key"}

    def get(self, item):
        if item == "userinfo":
            return UserInfoReponseMock()


class MVCOAuthTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_wtf import CSRFProtect
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_oauth")
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()
        self.csrf = CSRFProtect(self.app)
        self.appbuilder = AppBuilder(self.app)

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        users = db.session.query(User).filter(User.username.ilike("google%")).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        self.ctx.pop()

    def test_oauth_login(self):
        """
        OAuth: Test login
        """
        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        raw_state = {}
        state = jwt.encode(raw_state, "random_state", algorithm="HS256")

        with self.app.test_client() as client:
            with client.session_transaction() as session_:
                session_["oauth_state"] = "random_state"
            response = client.get(f"/oauth-authorized/google?state={state}")
            self.assertEqual(current_user.email, "user1@fab.org")
            self.assertEqual(response.location, "/")

    def test_oauth_login_invalid_state(self):
        """
        OAuth: Test login invalid state
        """
        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        raw_state = {}
        state = jwt.encode(raw_state, "random_state", algorithm="HS256")
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["oauth_state"] = "invalid_state"
            response = client.get(f"/oauth-authorized/google?state={state}")
            self.assertEqual(current_user.is_authenticated, False)
            self.assertEqual(response.location, "/login/")

    def test_oauth_login_unknown_provider(self):
        """
        OAuth: Test login with unknown provider
        """
        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        raw_state = {}
        state = jwt.encode(raw_state, "random_state", algorithm="HS256")
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["oauth_state"] = "random_state"

        response = client.get(f"/oauth-authorized/unknown_provider?state={state}")
        self.assertEqual(response.location, "/login/")

    def test_oauth_login_next(self):
        """
        OAuth: Test login next
        """
        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        raw_state = {"next": ["http://localhost/users/list/"]}
        state = jwt.encode(raw_state, "random_state", algorithm="HS256")
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["oauth_state"] = "random_state"
        response = client.get(f"/oauth-authorized/google?state={state}")
        self.assertEqual(response.location, "http://localhost/users/list/")

    def test_oauth_login_next_check(self):
        """
        OAuth: Test login next check
        """
        client = self.app.test_client()

        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        raw_state = {"next": ["ftp://sample"]}
        state = jwt.encode(raw_state, "random_state", algorithm="HS256")
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["oauth_state"] = "random_state"
        response = client.get(f"/oauth-authorized/google?state={state}")
        self.assertEqual(response.location, "/")

    def test_oauth_next_login_param(self):
        """
        OAuth: Test next quoted next_url param
        """
        self.appbuilder.sm.oauth_remotes = {"google": OAuthRemoteMock()}

        next_url = "http://localhost/data?param1=1&param2=2&param3="
        with self.app.test_client() as client:
            # use quote function to reproduce redirect to login
            response = client.get(
                f"/login/?next={quote(next_url)}", follow_redirects=True
            )
            self.assertTrue(quote(next_url) in response.text)
