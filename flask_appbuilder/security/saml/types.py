"""SAML TypedDict definitions for Flask-AppBuilder."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


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
