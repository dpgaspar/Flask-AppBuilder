from flask import current_app
from flask_appbuilder import ModelView, IndexView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import Contact, ContactGroup, Gender


def fill_gender():
    try:
        current_app.appbuilder.session.add(Gender(name="Male"))
        current_app.appbuilder.session.add(Gender(name="Female"))
        current_app.appbuilder.session.commit()
    except Exception:
        current_app.appbuilder.session.rollback()


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    label_columns = {"contact_group": "Contacts Group"}
    list_columns = ["name", "personal_celphone", "birthday", "contact_group.name"]

    base_order = ("name", "asc")

    show_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    add_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    edit_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class MyIndexView(IndexView):
    index_template = "my_index.html"
