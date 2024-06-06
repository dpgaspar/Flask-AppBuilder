from flask_appbuilder import ModelRestApi, ModelView
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.filters import BaseFilter
from marshmallow import fields, Schema
from sqlalchemy import or_

from .models import Contact, ContactGroup, ModelOMParent, ContactGroupTag


class GreetingsResponseSchema(Schema):
    message = fields.String()

class ContactGroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    list_columns = ["name", "created_by.first_name", "tags"]
    add_columns = ["name", "tags"]
    edit_columns = ["name", "tags"]

class ContactGroupTagModelView(ModelView):
    datamodel = SQLAInterface(ContactGroupTag)
    add_columns = ["name"]
    edit_columns = ["name"]
    list_columns = ["name"]

class GreetingApi(BaseApi):
    resource_name = "greeting"
    openapi_spec_component_schemas = (GreetingsResponseSchema,)

    openapi_spec_methods = {
        "greeting": {"get": {"description": "Override description"}}
    }

    @expose("/")
    def greeting(self):
        """Send a greeting
        ---
        get:
          responses:
            200:
              description: Greet the user
              content:
                application/json:
                  schema:
                    type: object
                    $ref: '#/components/schemas/GreetingsResponseSchema'
        """
        return self.response(200, message="Hello")


class CustomFilter(BaseFilter):
    name = "Custom Filter"
    arg_name = "opr"

    def apply(self, query, value):
        return query.filter(
            or_(Contact.name.like(value + "%"), Contact.address.like(value + "%"))
        )


class ContactModelApi(ModelRestApi):
    resource_name = "contact"
    datamodel = SQLAInterface(Contact)
    allow_browser_login = True
    list_columns = ["id", "name", "contact_group.id"]
    search_filters = {"name": [CustomFilter]}
    openapi_spec_methods = {
        "get_list": {"get": {"description": "Get all contacts, filter and pagination"}}
    }


class GroupModelApi(ModelRestApi):
    resource_name = "group"
    datamodel = SQLAInterface(ContactGroup)
    allow_browser_login = True
    list_columns = ["name", "tags.name", "created_by.first_name", "created_by.username"]


class ModelOMParentApi(ModelRestApi):
    allow_browser_login = True
    datamodel = SQLAInterface(ModelOMParent)
