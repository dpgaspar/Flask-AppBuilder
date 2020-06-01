from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.filters import BaseFilter
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
    list_columns = ["name", "year"]
    add_exclude_columns = ["address"]
    search_filters = {"name": [CustomFilter]}
    openapi_spec_methods = {
        "get_list": {
            "get": {
                "description": "Get all contacts, filter and pagination",
            }
        }
    }


appbuilder.add_api(ContactModelApi)


from marshmallow import Schema, ValidationError, fields, post_load
from marshmallow.validate import Length


def validate_name(n):
    print("----------- VALIDATE")
    if n[0] != "A":
        raise ValidationError("Name must start with an A")


class Model1CustomSchema(Schema):
    name = fields.String(validate=[Length(0, 25), validate_name])

    @post_load
    def process(self, data, **kwargs):
        return ContactGroup(**data)


class GroupModelApi(ModelRestApi):
    resource_name = "group"
    datamodel = SQLAInterface(ContactGroup)
    allow_browser_login = True
    #add_model_schema = Model1CustomSchema()
    validators_columns = {"name": validate_name}


appbuilder.add_api(GroupModelApi)


class ModelOMParentApi(ModelRestApi):
    allow_browser_login = True
    datamodel = SQLAInterface(ModelOMParent)


appbuilder.add_api(ModelOMParentApi)
