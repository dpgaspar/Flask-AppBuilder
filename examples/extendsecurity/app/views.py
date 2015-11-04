from flask import g
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterEqualFunction, FilterStartsWith
from app import db, appbuilder
from .models import ContactGroup, Gender, Contact, Company

def get_user_company():
    return g.user.company


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group.name','created_by.username']
    add_columns = ['name', 'address','birthday','personal_phone','personal_celphone','contact_group','gender']
    edit_columns = ['name', 'address','birthday','personal_phone','personal_celphone','contact_group','gender']
    base_order = ('name', 'asc')
    base_filters = [['created_by.company', FilterEqualFunction, get_user_company]]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)

db.create_all()
appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o")
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_separator("Contacts")

