import calendar
from flask import g
from flask_appbuilder import ModelView
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface

from . import appbuilder
from .models import ContactGroup, Contact, Tags


def get_user():
    return g.user.id


class ContactModelView(ModelView):
    datamodel = MongoEngineInterface(Contact)
    list_columns = ["name", "personal_celphone", "birthday", "contact_group.name"]


class GroupModelView(ModelView):
    datamodel = MongoEngineInterface(ContactGroup)
    related_views = [ContactModelView]
    search_columns = ["name"]


class TagsModelView(ModelView):
    datamodel = MongoEngineInterface(Tags)


class ContactChartView(GroupByChartView):
    datamodel = MongoEngineInterface(Contact)
    chart_title = "Grouped contacts"
    label_columns = ContactModelView.label_columns
    chart_type = "PieChart"

    definitions = [
        {"group": "contact_group", "series": [(aggregate_count, "contact_group")]},
        {"group": "gender", "series": [(aggregate_count, "gender")]},
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + " " + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = MongoEngineInterface(Contact)

    chart_title = "Grouped Birth contacts"
    chart_type = "AreaChart"
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            "group": "month_year",
            "formatter": pretty_month_year,
            "series": [(aggregate_count, "contact_group")],
        },
        {
            "group": "year",
            "formatter": pretty_year,
            "series": [(aggregate_count, "contact_group")],
        },
    ]


appbuilder.add_view(
    GroupModelView,
    "List Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    ContactModelView,
    "List Contacts",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    TagsModelView,
    "List Tags",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
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

appbuilder.security_cleanup()
