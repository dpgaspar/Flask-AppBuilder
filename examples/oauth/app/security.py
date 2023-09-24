from flask import session
from flask_appbuilder import expose
from flask_appbuilder.security.views import AuthOAuthView
from flask_appbuilder.security.sqla.manager import SecurityManager


class MyAuthOAuthView(AuthOAuthView):
    @expose("/logout/")
    def logout(self):
        """Delete access token before logging out."""
        session.pop("oauth_token", None)
        return super().logout()


class MySecurityManager(SecurityManager):
    authoauthview = MyAuthOAuthView

    def set_oauth_session(self, provider, oauth_response):
        """Store the ouath token in the session for later retrieval.

        In this example, the token is only required to send a tweet.
        """
        res = super().set_oauth_session(provider, oauth_response)
        # DON'T DO THIS IN PRODUCTION, SAVE TO A DB IN PRODUCTION
        if provider == "twitter":
            session["oauth_token"] = oauth_response
        return res
