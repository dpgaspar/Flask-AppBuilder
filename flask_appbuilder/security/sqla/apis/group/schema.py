from flask_appbuilder.security.sqla.models import Group
from marshmallow import fields, Schema
from marshmallow.validate import Length

name_description = "Group name"
label_description = "Group label"
description_description = "Group description"
roles_description = "Group roles"
users_description = "Group users"


class GroupPostSchema(Schema):
    model_cls = Group

    name = fields.String(
        required=True,
        validate=[Length(1, 100)],
        metadata={"description": name_description},
    )
    label = fields.String(
        required=False,
        allow_none=True,
        validate=[Length(0, 150)],
        metadata={"description": label_description},
    )
    description = fields.String(
        required=False,
        allow_none=True,
        validate=[Length(0, 512)],
        metadata={"description": description_description},
    )
    roles = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    users = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": users_description},
    )


class GroupPutSchema(Schema):
    model_cls = Group

    name = fields.String(
        required=False,
        validate=[Length(1, 100)],
        metadata={"description": name_description},
    )
    label = fields.String(
        required=False,
        allow_none=True,
        validate=[Length(0, 150)],
        metadata={"description": label_description},
    )
    description = fields.String(
        required=False,
        allow_none=True,
        validate=[Length(0, 512)],
        metadata={"description": description_description},
    )
    roles = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": roles_description},
    )
    users = fields.List(
        fields.Integer,
        required=False,
        metadata={"description": users_description},
    )
