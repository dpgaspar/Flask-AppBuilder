import calendar

from flask_appbuilder import GroupByChartView, ModelView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.widgets import (
    ListBlock, ListItem, ListLinkWidget, ListThumbnail, ShowBlockWidget
)


from . import appbuilder, db
from .models import Contact, ContactGroup, Gender


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

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


class ContactItemModelView(ContactModelView):
    list_title = "List Contact (Items)"
    list_widget = ListItem


class ContactThumbnailModelView(ContactModelView):
    list_title = "List Contact (Thumbnails)"
    list_widget = ListThumbnail


class ContactBlockModelView(ContactModelView):
    list_title = "List Contact (Blocks)"
    list_widget = ListBlock
    show_widget = ShowBlockWidget


class ContactLinkModelView(ContactModelView):
    list_title = "List Contact (Links)"
    list_widget = ListLinkWidget


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [
        ContactModelView,
        ContactItemModelView,
        ContactThumbnailModelView,
        ContactBlockModelView,
    ]


class ContactChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)
    chart_title = "Grouped contacts"
    label_columns = ContactModelView.label_columns
    chart_type = "PieChart"

    definitions = [
        {"group": "contact_group", "series": [(aggregate_count, "contact_group")]},
        {"group": "gender", "series": [(aggregate_count, "contact_group")]},
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + " " + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)

    chart_title = "Grouped Birth contacts"
    chart_type = "AreaChart"
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            "group": "month_year",
            "formatter": pretty_month_year,
            "series": [(aggregate_count, "group")],
        },
        {
            "group": "year",
            "formatter": pretty_year,
            "series": [(aggregate_count, "group")],
        },
    ]


db.create_all()
fill_gender()
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
appbuilder.add_view(
    ContactLinkModelView, "List Links Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    ContactItemModelView, "List Item Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    ContactBlockModelView,
    "List Block Contacts",
    icon="fa-envelope",
    category="Contacts",
)
appbuilder.add_view(
    ContactThumbnailModelView,
    "List Thumb Contacts",
    icon="fa-envelope",
    category="Contacts",
)
appbuilder.add_separator("Contacts")
appbuilder.add_view(
    ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts"
)
appbuilder.add_view(
    ContactTimeChartView,
    "Contacts Birth Chart",
    icon="fa-dashboard",
    category="Contacts",
)
