from marshmallow import fields, Schema


class ApiKeyPostSchema(Schema):
    name = fields.String(
        required=True,
        metadata={"description": "A friendly name for this API key"},
    )
    scopes = fields.String(
        load_default=None,
        metadata={"description": "Comma-separated scopes (optional)"},
    )
    expires_on = fields.DateTime(
        load_default=None,
        metadata={"description": "Expiration datetime in ISO format (optional)"},
    )


class ApiKeyResponseSchema(Schema):
    uuid = fields.String(metadata={"description": "Unique identifier for the key"})
    name = fields.String(metadata={"description": "Friendly name"})
    key_prefix = fields.String(metadata={"description": "Key prefix (e.g., sst_)"})
    scopes = fields.String(metadata={"description": "Comma-separated scopes"})
    active = fields.Boolean(metadata={"description": "Whether the key is active"})
    created_on = fields.DateTime(metadata={"description": "Creation timestamp"})
    expires_on = fields.DateTime(metadata={"description": "Expiration timestamp"})
    revoked_on = fields.DateTime(metadata={"description": "Revocation timestamp"})
    last_used_on = fields.DateTime(metadata={"description": "Last usage timestamp"})


class ApiKeyCreateResponseSchema(Schema):
    uuid = fields.String(metadata={"description": "Unique identifier for the key"})
    name = fields.String(metadata={"description": "Friendly name"})
    key = fields.String(
        metadata={"description": "The plaintext API key (only shown once at creation)"},
    )
    key_prefix = fields.String(metadata={"description": "Key prefix (e.g., sst_)"})
    scopes = fields.String(metadata={"description": "Comma-separated scopes"})
    created_on = fields.DateTime(metadata={"description": "Creation timestamp"})
    expires_on = fields.DateTime(metadata={"description": "Expiration timestamp"})
