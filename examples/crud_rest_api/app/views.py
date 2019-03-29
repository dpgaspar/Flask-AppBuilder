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


class ContactModelApi(ModelRestApi):
    resource_name = 'contact'
    datamodel = SQLAInterface(Contact)


appbuilder.add_api(ContactModelApi)


class GroupModelApi(ModelRestApi):
    resource_name = 'group'
    datamodel = SQLAInterface(ContactGroup)


appbuilder.add_api(GroupModelApi)
