from flask_appbuilder.security.sqla.models import User
from marshmallow import fields, Schema, validates_schema, ValidationError
from marshmallow.validate import Length

from .validator import PasswordComplexityValidator

active_description = (
    "Is user active?" "It's not a good policy to remove a user, just make it inactive"
)
email_description = "The user's email"
first_name_description = "The user's first name"
last_name_description = "The user's last name"
password_description = "The user's password for authentication"
roles_description = "The user's roles"
username_description = "The user's username"


class UserPostSchema(Schema):
    model_cls = User
    active = fields.Boolean(
        required=False, dump_default=True, metadata={"description": active_description}
    )
    email = fields.String(required=True, metadata={"description": email_description})
    first_name = fields.String(
        required=True, metadata={"description": first_name_description}
    )
    last_name = fields.String(
        required=True, metadata={"description": last_name_description}
    )
    password = fields.String(
        required=True,
        validate=[PasswordComplexityValidator()],
        metadata={"description": password_description},
    )
    roles = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    groups = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    username = fields.String(
        required=True,
        validate=[Length(1, 250)],
        metadata={"description": username_description},
    )

    @validates_schema
    def validate_roles_or_groups_present(self, data, **kwargs):
        """
        Ensure at least one of 'roles' or 'groups' is present and non-empty.
        """
        roles = data.get("roles") or []
        groups = data.get("groups") or []

        if not roles and not groups:
            raise ValidationError(
                "At least one of 'roles' or 'groups' must be provided and non-empty."
            )


class UserPutSchema(Schema):
    model_cls = User

    active = fields.Boolean(
        required=False, metadata={"description": active_description}
    )
    email = fields.String(required=False, metadata={"description": email_description})
    first_name = fields.String(
        required=False, metadata={"description": first_name_description}
    )
    last_name = fields.String(
        required=False, metadata={"description": last_name_description}
    )
    password = fields.String(
        required=False,
        validate=[PasswordComplexityValidator()],
        metadata={"description": password_description},
    )
    roles = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    groups = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    username = fields.String(
        required=False,
        validate=[Length(1, 250)],
        metadata={"description": username_description},
    )
