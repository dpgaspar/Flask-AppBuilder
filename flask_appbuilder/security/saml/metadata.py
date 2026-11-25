"""SP metadata generation for SAML authentication."""

from __future__ import annotations

import logging
from typing import Any, Dict

log = logging.getLogger(__name__)


def get_sp_metadata(saml_settings: Dict[str, Any]) -> str:
    """
    Generate SP metadata XML from SAML settings.

    :param saml_settings: The python3-saml settings dict
    :return: SP metadata XML string
    """
    from onelogin.saml2.settings import OneLogin_Saml2_Settings

    settings = OneLogin_Saml2_Settings(saml_settings, sp_validation_only=True)
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if errors:
        log.error("SP Metadata validation errors: %s", errors)
        raise ValueError(f"SP Metadata validation errors: {errors}")
    return metadata
