import os

from flask_appbuilder.security.manager import AUTH_OID

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI"
) or "sqlite:///" + os.path.join(basedir, "app.db")

SECRET_KEY = "thisismyscretkey"

AUTH_TYPE = AUTH_OID

OPENID_PROVIDERS = [
    {"name": "Google", "url": "https://www.google.com/accounts/o8/id"},
    {"name": "Yahoo", "url": "https://me.yahoo.com"},
    {"name": "AOL", "url": "http://openid.aol.com/<username>"},
    {"name": "Flickr", "url": "http://www.flickr.com/<username>"},
    {"name": "OpenStack", "url": "https://openstackid.org/"},
]

WTF_CSRF_ENABLED = False

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role for all users
AUTH_USER_REGISTRATION_ROLE = "Admin"
