from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import BaseApi, expose, safe, protect, rison
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.filters import BaseFilter
from marshmallow import Schema, fields
from sqlalchemy import or_

from . import appbuilder, db
from .models import Contact, ContactGroup, Gender, ModelOMParent


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.add(Gender(name="Nonbinary"))
        db.session.commit()
    except Exception:
        db.session.rollback()


db.create_all()
fill_gender()


class GreetingApi(BaseApi):
    resource_name = "greeting"
    openapi_spec_methods = {
        "greeting": {
            "get": {
                "description": "Override description",
            }
        }
    }

    @expose('/')
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
                    properties:
                      message:
                        type: string
        """
        return self.response(200, message="Hello")


appbuilder.add_api(GreetingApi)


sum_schema = {
    "type": "object",
    "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
}


class MathApi(BaseApi):
    apispec_parameter_schemas = {"sum_schema": sum_schema}
    allow_browser_login = True

    @expose("/sum")
    @protect()
    @safe
    @rison(sum_schema)
    def sum(self, **kwargs):
        """
        ---
        get:
          description: Sum two numbers
          parameters:
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/sum_schema'
          responses:
            200:
              description: Sum two numbers
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: number
        """
        query_parameters = kwargs["rison"]
        return self.response(200, message=query_parameters["a"] + query_parameters["b"])


appbuilder.add_api(MathApi)


class CustomFilter(BaseFilter):
    name = "Custom Filter"
    arg_name = "opr"

    def apply(self, query, value):
        return query.filter(
            or_(
                Contact.name.like(value + "%"),
                Contact.address.like(value + "%"),
            )
        )


class ContactModelApi(ModelRestApi):
    resource_name = "contact"
    datamodel = SQLAInterface(Contact)
    allow_browser_login = True

    search_filters = {"name": [CustomFilter]}
    openapi_spec_methods = {
        "get_list": {
            "get": {
                "description": "Get all contacts, filter and pagination",
            }
        }
    }


appbuilder.add_api(ContactModelApi)


class GroupModelApi(ModelRestApi):
    resource_name = "group"
    datamodel = SQLAInterface(ContactGroup)
    allow_browser_login = True


appbuilder.add_api(GroupModelApi)


class ModelOMParentApi(ModelRestApi):
    allow_browser_login = True
    datamodel = SQLAInterface(ModelOMParent)


appbuilder.add_api(ModelOMParentApi)
