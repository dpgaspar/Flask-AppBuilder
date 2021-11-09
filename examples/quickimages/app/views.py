from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import ModelView

from . import appbuilder, db
from .models import Person, PersonGroup


class PersonModelView(ModelView):
    datamodel = SQLAInterface(Person, db.session)

    list_title = "List Contacts"
    show_title = "Show Contact"
    add_title = "Add Contact"
    edit_title = "Edit Contact"

    # list_widget = ListThumbnail

    label_columns = {
        "person_group_id": "Group",
        "photo_img": "Photo",
        "photo_img_thumbnail": "Photo",
    }
    list_columns = [
        "photo_img_thumbnail",
        "name",
        "personal_celphone",
        "business_celphone",
        "birthday",
        "person_group",
    ]

    show_fieldsets = [
        ("Summary", {"fields": ["photo_img", "name", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]

    add_fieldsets = [
        ("Summary", {"fields": ["name", "photo", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]

    edit_fieldsets = [
        ("Summary", {"fields": ["name", "photo", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(PersonGroup, db.session)
    related_views = [PersonModelView]

    label_columns = {"phone1": "Phone (1)", "phone2": "Phone (2)", "taxid": "Tax ID"}
    list_columns = ["name", "notes"]


class PersonChartView(GroupByChartView):
    datamodel = SQLAInterface(Person)
    chart_title = "Grouped Persons"
    label_columns = PersonModelView.label_columns
    chart_type = "PieChart"

    definitions = [
        {"group": "person_group", "series": [(aggregate_count, "person_group")]}
    ]


db.create_all()
appbuilder.add_view(
    GroupModelView(), "List Groups", icon="fa-folder-open-o", category="Contacts"
)
appbuilder.add_view(
    PersonModelView(), "List Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    PersonChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts"
)
