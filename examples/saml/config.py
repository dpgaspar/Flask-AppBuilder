"""Example configuration for SAML authentication with Flask-AppBuilder.

Demonstrates configuring FAB with SAML / Microsoft Entra ID authentication.
Adjust the IdP settings to match your identity provider.

Required environment variables:
    SAML_TENANT_ID  - Microsoft Entra ID tenant ID
    SAML_IDP_CERT   - IdP signing certificate (base64 content, no PEM headers)
"""

import os

from flask_appbuilder.const import AUTH_SAML

basedir = os.path.abspath(os.path.dirname(__file__))

# Entra ID tenant ID and IdP certificate from environment
SAML_TENANT_ID = os.environ.get("SAML_TENANT_ID", "<YOUR_TENANT_ID>")
SAML_IDP_CERT = os.environ.get("SAML_IDP_CERT", "<YOUR_IDP_CERTIFICATE>")

# Flask secret key
SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

# Database connection
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")

# Flask-AppBuilder Security
AUTH_TYPE = AUTH_SAML

# Set to True to allow user self registration via SAML
AUTH_USER_REGISTRATION = True

# Default role for self-registered users
AUTH_USER_REGISTRATION_ROLE = "Admin"

# Sync roles at login (maps SAML groups/roles to FAB roles)
AUTH_ROLES_SYNC_AT_LOGIN = True

# Role mapping from SAML group names to FAB role names
AUTH_ROLES_MAPPING = {
    "admins": ["Admin"],
    "users": ["Public"],
}

# -------------------------------------------------------
# SAML Configuration
# -------------------------------------------------------

# List of SAML Identity Providers
# Replace <TENANT_ID> with your Microsoft Entra ID (formerly Azure AD) tenant ID.
# You can find these values in the Azure Portal under:
#   Entra ID > Enterprise Applications > Your App > Single sign-on
SAML_PROVIDERS = [
    {
        "name": "entra_id",
        "icon": "fa-microsoft",
        # IdP configuration from Entra ID SAML metadata:
        # https://login.microsoftonline.com/<TENANT_ID>/federationmetadata/2007-06/federationmetadata.xml
        "idp": {
            "entityId": f"https://sts.windows.net/{SAML_TENANT_ID}/",
            "singleSignOnService": {
                "url": f"https://login.microsoftonline.com/{SAML_TENANT_ID}/saml2",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": f"https://login.microsoftonline.com/{SAML_TENANT_ID}/saml2",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": SAML_IDP_CERT,
        },
        # Map SAML assertion attributes to FAB user fields.
        # Left side: SAML attribute name (Entra ID claim URIs).
        # Right side: FAB user field name.
        "attribute_mapping": {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "email",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "first_name",  # noqa: E501
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "last_name",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "username",
            "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups": "role_keys",
        },
    },
]

# Global SAML Service Provider configuration
SAML_CONFIG = {
    "strict": False,
    "debug": True,
    "sp": {
        "entityId": "http://localhost:9000/saml/metadata/",
        "assertionConsumerService": {
            "url": "http://localhost:9000/saml/acs/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        },
        "singleLogoutService": {
            "url": "http://localhost:9000/saml/slo/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        # SP certificate (optional, needed for signed requests)
        "x509cert": "",
        # "privateKey": "",
    },
    "security": {
        "nameIdEncrypted": False,
        "authnRequestsSigned": False,
        "logoutRequestSigned": False,
        "logoutResponseSigned": False,
        "signMetadata": False,
        "wantMessagesSigned": False,
        "wantAssertionsSigned": True,
        "wantAssertionsEncrypted": False,
        "wantNameId": True,
        "wantNameIdEncrypted": False,
        "wantAttributeStatement": True,
    },
}
