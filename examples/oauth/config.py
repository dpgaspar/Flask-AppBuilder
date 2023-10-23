import os
from flask import session
from flask_appbuilder.security.manager import AUTH_OAUTH

basedir = os.path.abspath(os.path.dirname(__file__))

# Your App secret key
SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# ------------------------------
# GLOBALS FOR APP Builder
# ------------------------------
# Uncomment to setup Your App name
# APP_NAME = "My App Name"

# Uncomment to setup Setup an App icon
# APP_ICON = "static/img/logo.jpg"

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database (username/password()
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server
AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        "name": "twitter",
        "icon": "fa-twitter",
        "remote_app": {
            "client_id": os.environ.get("TWITTER_KEY"),
            "client_secret": os.environ.get("TWITTER_SECRET"),
            "api_base_url": "https://api.twitter.com/1.1/",
            "request_token_url": "https://api.twitter.com/oauth/request_token",
            "access_token_url": "https://api.twitter.com/oauth/access_token",
            "authorize_url": "https://api.twitter.com/oauth/authenticate",
            "fetch_token": lambda: session.get(
                "oauth_token"
            ),  # DON'T DO THIS IN PRODUCTION
        },
    },
    {
        "name": "google",
        "icon": "fa-google",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("GOOGLE_KEY"),
            "client_secret": os.environ.get("GOOGLE_SECRET"),
            "api_base_url": "https://www.googleapis.com/oauth2/v2/",
            "client_kwargs": {"scope": "email profile"},
            "request_token_url": None,
            "access_token_url": "https://accounts.google.com/o/oauth2/token",
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
            "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
        },
    },
    {
        "name": "azure",
        "icon": "fa-windows",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("AZURE_APPLICATION_ID"),
            "client_secret": os.environ.get("AZURE_SECRET"),
            "api_base_url": f"https://login.microsoftonline.com/{os.environ.get('AZURE_TENANT_ID')}/oauth2",
            "client_kwargs": {
                "scope": "User.read name preferred_username email profile upn",
                "resource": os.environ.get("AZURE_APPLICATION_ID"),
            },
            "request_token_url": None,
            "access_token_url": f"https://login.microsoftonline.com/"
            f"{os.environ.get('AZURE_TENANT_ID')}/"
            "oauth2/token",
            "authorize_url": f"https://login.microsoftonline.com/"
            f"{os.environ.get('AZURE_TENANT_ID')}/"
            f"oauth2/authorize",
        },
    },
    {
        "name": "okta",
        "icon": "fa-circle-o",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("OKTA_KEY"),
            "client_secret": os.environ.get("OKTA_SECRET"),
            "api_base_url": f"https://{os.environ.get('OKTA_DOMAIN')}.okta.com/oauth2/v1/",
            "client_kwargs": {"scope": "openid profile email groups"},
            "access_token_url": f"https://{os.environ.get('OKTA_DOMAIN')}.okta.com/"
            f"oauth2/v1/token",
            "authorize_url": f"https://{os.environ.get('OKTA_DOMAIN')}.okta.com/"
            f"oauth2/v1/authorize",
            "server_metadata_url": f"https://{os.environ.get('OKTA_DOMAIN')}.okta.com/"
            f".well-known/openid-configuration",
        },
    },
    {
        "name": "keycloak",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("KEYCLOAK_CLIENT_ID"),
            "client_secret": os.environ.get("KEYCLOAK_CLIENT_SECRET"),
            "api_base_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"realms/master/protocol/openid-connect",
            "client_kwargs": {"scope": "email profile"},
            "access_token_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"realms/master/protocol/openid-connect/token",
            "authorize_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"realms/master/protocol/openid-connect/auth",
            "request_token_url": None,
        },
    },
    {
        "name": "keycloak_before_17",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("KEYCLOAK_CLIENT_ID"),
            "client_secret": os.environ.get("KEYCLOAK_CLIENT_SECRET"),
            "api_base_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"auth/realms/master/protocol/openid-connect",
            "client_kwargs": {"scope": "email profile"},
            "access_token_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"auth/realms/master/protocol/openid-connect/token",
            "authorize_url": f"https://{os.environ.get('KEYCLOAK_DOMAIN')}/"
            f"auth/realms/master/protocol/openid-connect/auth",
            "request_token_url": None,
        },
    },
]

# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role for all users
AUTH_USER_REGISTRATION_ROLE = "Admin"

# Self registration role based on user info
# AUTH_USER_REGISTRATION_ROLE_JMESPATH = "contains(['alice@example.com', 'celine@example.com'], email) && 'Admin' || 'Public'"

# Replace users database roles each login with those received from OAUTH/LDAP
AUTH_ROLES_SYNC_AT_LOGIN = True

# A mapping from LDAP/OAUTH group names to FAB roles
AUTH_ROLES_MAPPING = {
    # For OAUTH
    # "USER_GROUP_NAME": ["User"],
    # "ADMIN_GROUP_NAME": ["Admin"],
    # For LDAP
    # "cn=User,ou=groups,dc=example,dc=com": ["User"],
    # "cn=Admin,ou=groups,dc=example,dc=com": ["Admin"],
}

# When using LDAP Auth, setup the ldap server
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"
# AUTH_LDAP_USE_TLS = False

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
# Setup default language
BABEL_DEFAULT_LOCALE = "en"
# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
}
# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
# The file upload folder, when using models with files
UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/uploads/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

# Theme configuration
# these are located on static/appbuilder/css/themes
# you can create your own and easily use them placing them on the same dir structure to override
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "cerulean.css"
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"

FAB_SECURITY_MANAGER_CLASS = "app.security.MySecurityManager"
