from flask import g
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask_appbuilder.models.sqla.interface import SQLAInterface

from . import appbuilder
from .models import Company, Contact, ContactGroup


def get_user_company():
    return g.user.company


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_columns = [
        "name",
        "personal_celphone",
        "birthday",
        "contact_group.name",
        "created_by.username",
    ]
    add_columns = [
        "name",
        "address",
        "birthday",
        "personal_phone",
        "personal_celphone",
        "contact_group",
        "gender",
    ]
    edit_columns = [
        "name",
        "address",
        "birthday",
        "personal_phone",
        "personal_celphone",
        "contact_group",
        "gender",
    ]
    base_order = ("name", "asc")
    base_filters = [["created_by.company", FilterEqualFunction, get_user_company]]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)
