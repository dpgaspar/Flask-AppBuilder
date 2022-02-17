from marshmallow import fields, Schema, validate, validates_schema
from .validator import PasswordComplexityValidator
from marshmallow.validate import Length

class UserPostSchema(Schema):
    active = fields.Boolean(default=False)
    email = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password = fields.String(required=True, validate=[PasswordComplexityValidator()])
    roles = fields.List(fields.Integer, required=True, validate = [Length(1)])
    username = fields.String(required=True, validate = [Length(1,250)])

class UserPutSchema(Schema):
    active = fields.Boolean(default=False)
    email = fields.String(required=False)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    password = fields.String(required=False, validate=[PasswordComplexityValidator()])
    roles = fields.List(fields.Integer, required=False, validate = [Length(1)])
    username = fields.String(required=False, validate = [Length(1,250)])
