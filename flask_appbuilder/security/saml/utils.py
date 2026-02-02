"""SAML utility helpers for Flask-AppBuilder."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict

from flask import request

log = logging.getLogger(__name__)


class SAMLServiceBinding(TypedDict):
    url: str
    binding: str


class SAMLIdPConfig(TypedDict, total=False):
    entityId: str
    singleSignOnService: SAMLServiceBinding
    singleLogoutService: SAMLServiceBinding
    x509cert: str


class SAMLProvider(TypedDict, total=False):
    name: str
    icon: str
    idp: SAMLIdPConfig
    attribute_mapping: Dict[str, str]


class SAMLSPConfig(TypedDict, total=False):
    entityId: str
    assertionConsumerService: SAMLServiceBinding
    singleLogoutService: SAMLServiceBinding
    NameIDFormat: str
    x509cert: str
    privateKey: str


class SAMLSecurityConfig(TypedDict, total=False):
    nameIdEncrypted: bool
    authnRequestsSigned: bool
    logoutRequestSigned: bool
    logoutResponseSigned: bool
    signMetadata: bool
    wantMessagesSigned: bool
    wantAssertionsSigned: bool
    wantAssertionsEncrypted: bool
    wantNameId: bool
    wantNameIdEncrypted: bool
    wantAttributeStatement: bool


class SAMLConfig(TypedDict, total=False):
    strict: bool
    debug: bool
    sp: SAMLSPConfig
    idp: SAMLIdPConfig
    security: SAMLSecurityConfig


class SAMLFlaskRequest(TypedDict):
    https: str
    http_host: str
    server_port: str
    script_name: str
    get_data: Dict[str, Any]
    post_data: Dict[str, Any]
    query_string: str


class SAMLUserInfo(TypedDict, total=False):
    username: str
    email: str
    first_name: str
    last_name: str
    role_keys: List[str]


def map_saml_attributes(
    saml_attributes: Dict[str, List[str]],
    attribute_mapping: Dict[str, str],
    name_id: Optional[str] = None,
) -> SAMLUserInfo:
    """Map SAML assertion attributes to FAB user fields.

    Args:
        saml_attributes: Raw attributes from the SAML assertion.
        attribute_mapping: Mapping of SAML attribute names to FAB field names.
        name_id: The SAML NameID value (used as fallback for username/email).

    Returns:
        Dictionary with FAB user field names as keys.
    """
    userinfo: Dict[str, Any] = {}

    for saml_attr, fab_field in attribute_mapping.items():
        value = saml_attributes.get(saml_attr)
        if value is None:
            continue
        if fab_field == "role_keys":
            userinfo[fab_field] = list(value)
        else:
            userinfo[fab_field] = value[0] if value else ""

    # Fallback to NameID if no username/email mapped
    if name_id and "username" not in userinfo:
        userinfo["username"] = name_id
        if "@" in name_id and "email" not in userinfo:
            userinfo["email"] = name_id

    return userinfo


def fetch_idp_metadata(url: str) -> str:
    """Fetch IdP metadata XML from a remote URL."""
    import requests

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def prepare_flask_request() -> SAMLFlaskRequest:
    """Prepare the Flask request data in the format expected by python3-saml."""
    return {
        "https": "on" if request.scheme == "https" else "off",
        "http_host": request.host,
        "server_port": request.environ.get("SERVER_PORT", "443"),
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
        "query_string": request.query_string.decode("utf-8"),
    }
