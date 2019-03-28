from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from . import db, appbuilder
from .models import ContactGroup, Gender, Contact


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


db.create_all()
fill_gender()


class ContactModelView(ModelRestApi):
    resource_name = 'contact'
    datamodel = SQLAInterface(Contact)


appbuilder.add_view(
    ContactModelView,
    "List Contacts",
    icon="fa-envelope",
    category="Contacts"
)


class GroupModelView(ModelRestApi):
    resource_name = 'group'
    datamodel = SQLAInterface(ContactGroup)


appbuilder.add_view(
    GroupModelView,
    "List Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon='fa-envelope'
)

