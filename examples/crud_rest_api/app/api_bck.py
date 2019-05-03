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
    class_permission_name = "api"
    previous_class_permission_name = "ContactModelApi"
    datamodel = SQLAInterface(Contact)
    allow_browser_login = True

    method_permission_name = {"get_list": "read",
                              "get": "read",
                              "info": "read"}
    previous_method_permission_name = {"get_list": "get",
                                       "get": "get",
                                       "info": "info"}


appbuilder.add_api(ContactModelApi)



class GroupModelApi(ModelRestApi):
    resource_name = "group"
    class_permission_name = "api"
    previous_class_permission_name = "GroupModelApi"
    datamodel = SQLAInterface(ContactGroup)
    allow_browser_login = True

    method_permission_name = {"get_list": "read",
                              "get": "read",
                              "info": "read"}
    previous_method_permission_name = {"get_list": "get",
                                       "get": "get",
                                       "info": "info"}

appbuilder.add_api(GroupModelApi)

