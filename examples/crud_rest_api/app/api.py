from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface

from . import appbuilder, db
from .models import Contact, ContactGroup, Gender


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()


db.create_all()
fill_gender()


class ContactModelApi(ModelRestApi):
    resource_name = "contact"
    datamodel = SQLAInterface(Contact)
    allow_browser_login = True


appbuilder.add_api(ContactModelApi)


class GroupModelApi(ModelRestApi):
    resource_name = "group"
    datamodel = SQLAInterface(ContactGroup)
    allow_browser_login = True


appbuilder.add_api(GroupModelApi)
