from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import MasterDetailView
from flask_babel import lazy_gettext as _

from . import appbuilder, db
from .models import Contact, ContactGroup, Gender


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()


class ContactGeneralView(ModelView):
    datamodel = SQLAInterface(Contact)

    label_columns = {"contact_group": "Contacts Group"}
    list_columns = ["name", "personal_phone", "contact_group"]

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


class GroupMasterView(MasterDetailView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactGeneralView]


class GroupGeneralView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactGeneralView]


fixed_translations_import = [
    _("List Groups"),
    _("Manage Groups"),
    _("List Contacts"),
    _("Contacts Chart"),
    _("Contacts Birth Chart"),
]

db.create_all()
fill_gender()
appbuilder.add_view(
    GroupMasterView, "List Groups", icon="fa-folder-open-o", category="Contacts"
)
appbuilder.add_separator("Contacts")
appbuilder.add_view(
    GroupGeneralView, "Manage Groups", icon="fa-folder-open-o", category="Contacts"
)
appbuilder.add_view(
    ContactGeneralView, "List Contacts", icon="fa-envelope", category="Contacts"
)
