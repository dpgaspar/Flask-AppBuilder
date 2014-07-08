import calendar
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.views import GroupModelView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.charts.views import GroupByChartView
from flask.ext.appbuilder.models.group import aggregate_count
from flask.ext.babelpkg import lazy_gettext as _
from flask.ext.appbuilder.models.generic import PSSession
from flask_appbuilder.models.generic.interface import VolInterface
from flask_appbuilder.models.generic import PSModel

from app import db, appbuilder
from .models import Group, Gender, Contact


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()

sess = PSSession()


class VolView(ModelView):
    datamodel = VolInterface(PSModel(), sess)
    base_permission = ['can_list']
    search_columns = ['UID']

class ContactModelView(ModelView):
    datamodel = SQLAModel(Contact)

    label_columns = {'group': 'Contacts Group'}
    list_columns = ['name', 'personal_celphone', 'birthday', 'group']

    list_template = 'list_contacts.html'
    show_template = 'show_contacts.html'

    base_order = ('name', 'asc')

    show_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

class ContactGroupModelView(GroupModelView):
    datamodel = SQLAModel(Contact)
    group_bys_cols = ['group']
    # ['<COLNAME>',<FUNC>, ....]
    aggr_by_cols = [(aggregate_count, 'name')]
    # [(<AGGR FUNC>,'<COLNAME>'),...]
    formatter_by_cols = {}
    # {<FUNC>: '<COLNAME>',...}


class GroupModelView(ModelView):
    datamodel = SQLAModel(Group)
    related_views = [ContactModelView]
    show_template = 'appbuilder/general/model/show_cascade.html'

class ContactChartView(GroupByChartView):
    datamodel = SQLAModel(Contact)
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group' : 'group',
            'series' : [(aggregate_count,'group')]
        },
        {
            'group' : 'gender',
            'series' : [(aggregate_count,'group')]
        }
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)

def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAModel(Contact)

    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            'group' : 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count,'group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count,'group')]
        }
    ]




db.create_all()
fill_gender()

appbuilder.add_view(VolView(), "List PS", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(ContactGroupModelView, "List Grouped Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

