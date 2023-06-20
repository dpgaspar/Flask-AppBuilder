from marshmallow import fields, Schema


class RolePermissionPostSchema(Schema):
    permission_view_menu_ids = fields.List(
        fields.Integer,
        required=True,
        metadata={"description": "List of permission view menu id"},
    )


class RolePermissionListSchema(Schema):
    id = fields.Integer()
    permission_name = fields.String()
    view_menu_name = fields.String()
