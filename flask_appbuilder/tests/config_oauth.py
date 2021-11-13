import os

from flask_appbuilder.security.manager import AUTH_OAUTH

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI"
) or "sqlite:///" + os.path.join(basedir, "app.db")

SECRET_KEY = "thisismyscretkey"

AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        "name": "google",
        "icon": "fa-google",
        "token_key": "access_token",
        "remote_app": {
            "client_id": "CLIENT_ID",
            "client_secret": "CLIENT_SECRET",
            "api_base_url": "https://www.googleapis.com/oauth2/v2/",
            "client_kwargs": {"scope": "email profile"},
            "request_token_url": None,
            "access_token_url": "https://accounts.google.com/o/oauth2/token",
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        },
    }
]

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role for all users
AUTH_USER_REGISTRATION_ROLE = "Admin"
