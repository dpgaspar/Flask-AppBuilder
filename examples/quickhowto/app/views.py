import calendar
from flask_appbuilder import ModelView
from flask_appbuilder.views import redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_babel import lazy_gettext as _
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction

from . import db, appbuilder, app
from .models import ContactGroup, Gender, Contact, ContactGroupSchema, ContactSchema, GroupCustomSchema


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    def post_add_redirect(self):
        return redirect('model1viewwithredirects/show/{0}'.format(99999))

    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group.name']

    base_order = ('name', 'asc')
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class GroupModelRestApi(ModelRestApi):
    resource_name = 'group'
    add_model_schema = GroupCustomSchema()
    edit_model_schema = GroupCustomSchema()
    datamodel = SQLAInterface(ContactGroup)


class ContactModelRestApi(ModelRestApi):
    resource_name = 'contact'
    datamodel = SQLAInterface(Contact)
    list_columns = ['name', 'contact_group']
    base_filters = [['contact_group.name', FilterStartsWith, 'F']]
    #list_model_schema = ContactSchema()
    #base_filters = [['name', FilterStartsWith, 'a']]
    #add_query_rel_fields = {
    #    'contact_group': [['name', FilterStartsWith, 'F']]
    #}
    #edit_query_rel_fields = {
    #    'contact_group': [['name', FilterStartsWith, 'F']]
    #}

    #list_columns = ['name', 'address', 'personal_celphone']
    #base_order = ('name', 'desc')
    #list_exclude_columns = ['gender', 'contact_group_id','gender_id', 'id']
    #show_exclude_columns = ['name']


class ContactChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group' : 'contact_group',
            'series' : [(aggregate_count,'contact_group')]
        },
        {
            'group' : 'gender',
            'series' : [(aggregate_count,'contact_group')]
        }
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)

    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            'group' : 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'group')]
        }
    ]


db.create_all()
fill_gender()
appbuilder.add_view_no_menu(GroupModelRestApi)
appbuilder.add_view_no_menu(ContactModelRestApi)

appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

