from typing import Union

from flask import current_app
from flask_appbuilder.const import (
    API_SECURITY_PROVIDER_DB,
    API_SECURITY_PROVIDER_LDAP,
    AUTH_DB,
    AUTH_LDAP,
)
from marshmallow import fields, Schema, ValidationError
from marshmallow.validate import Length, OneOf


provider_to_auth_type = {"db": AUTH_DB, "ldap": AUTH_LDAP}


def validate_password(value: Union[bytes, bytearray, str]) -> None:
    if value and sum(value.encode()) == 0:
        raise ValidationError("Password null is not allowed")


def validate_provider(value: Union[bytes, bytearray, str]) -> None:
    if not current_app.appbuilder.sm.api_login_allow_multiple_providers:
        provider_name = current_app.appbuilder.sm.auth_type_provider_name
        if provider_name and provider_name != value:
            raise ValidationError("Alternative authentication provider is not allowed")


class LoginPost(Schema):
    username = fields.String(required=True, allow_none=False, validate=Length(min=1))
    password = fields.String(
        validate=[Length(min=1), validate_password], required=True, allow_none=False
    )
    provider = fields.String(
        validate=[
            OneOf([API_SECURITY_PROVIDER_DB, API_SECURITY_PROVIDER_LDAP]),
            validate_provider,
        ]
    )
    refresh = fields.Boolean(required=False)


login_post = LoginPost()
