import os

from flask_appbuilder.const import AUTH_DB
from flask_appbuilder.exceptions import PasswordComplexityValidationError

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

OPENID_PROVIDERS = [
    {"name": "Google", "url": "https://www.google.com/accounts/o8/id"},
    {"name": "Yahoo", "url": "https://me.yahoo.com"},
    {"name": "AOL", "url": "http://openid.aol.com/<username>"},
    {"name": "Flickr", "url": "http://www.flickr.com/<username>"},
    {"name": "MyOpenID", "url": "https://www.myopenid.com"},
]

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
# SQLALCHEMY_DATABASE_URI = 'mysql://username:password@mysqlserver.local/quickhowto'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://pguser:pguserpassword@127.0.0.1:5432/app'
# SQLALCHEMY_ECHO = True
SQLALCHEMY_POOL_RECYCLE = 3

BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_FOLDER = "translations"
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "fr": {"flag": "fr", "name": "French"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
    "el": {"flag": "gr", "name": "Greek"},
    "ja_JP": {"flag": "jp", "name": "Japanese"},
}

FAB_API_MAX_PAGE_SIZE = 100


def custom_password_validator(password: str) -> None:
    """
    A simplistic example for a password validator
    """
    if len(password) < 8:
        raise PasswordComplexityValidationError("Must have at least 8 characters")


# FAB_PASSWORD_COMPLEXITY_VALIDATOR = custom_password_validator

FAB_PASSWORD_COMPLEXITY_ENABLED = False

# ------------------------------
# GLOBALS FOR GENERAL APP's
# ------------------------------
UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_URL = "/static/uploads/"
AUTH_TYPE = AUTH_DB
# AUTH_LDAP_SERVER = "ldap://dc.domain.net"
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
APP_NAME = "F.A.B. Example"
APP_THEME = ""  # default
# APP_THEME = "cerulean.css"      # COOL
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"       # COOL
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"          # COOL
# APP_THEME = "spacelab.css"      # NICE
# APP_THEME = "united.css"
# APP_THEME = "darkly.css"
# APP_THEME = "lumen.css"
# APP_THEME = "paper.css"
# APP_THEME = "sandstone.css"
# APP_THEME = "solar.css"
# APP_THEME = "superhero.css"
