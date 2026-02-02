"""SAML utility helpers for Flask-AppBuilder."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .types import SAMLUserInfo

log = logging.getLogger(__name__)


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