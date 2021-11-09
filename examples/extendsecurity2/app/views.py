from flask import g
from flask_appbuilder import ModelView
from flask_appbuilder.models.filters import BaseFilter
from flask_appbuilder.models.sqla.filters import get_field_setup_query
from flask_appbuilder.models.sqla.interface import SQLAInterface

from . import appbuilder, db
from .models import Company, Contact, ContactGroup
from .sec_views import UserDBModelView


class FilterInManyFunction(BaseFilter):
    name = "Filter view where field is in a list returned by a function"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.any(Company.id.in_(func())))


def get_user_companies():
    return set([company.id for company in g.user.companies])
    return g.user.companies


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_columns = [
        "name",
        "personal_celphone",
        "birthday",
        "contact_group.name",
        "created_by",
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
    base_filters = [["created_by.companies", FilterInManyFunction, get_user_companies]]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)
    list_columns = ["name", "myuser"]
    related_views = [UserDBModelView]


db.create_all()
appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o")
appbuilder.add_view(
    GroupModelView,
    "List Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_separator("Contacts")
