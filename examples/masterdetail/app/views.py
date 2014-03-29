from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView, MasterDetailView
from flask.ext.appbuilder.charts.views import ChartView, TimeChartView
from flask.ext.babelpkg import lazy_gettext as _

from app import app, db
from models import Group, Gender, Contact


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


class ContactGeneralView(GeneralView):
    datamodel = SQLAModel(Contact, db.session)

    label_columns = {'group': 'Contacts Group'}
    list_columns = ['name', 'personal_phone', 'group']

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


class GroupGeneralView(MasterDetailView):
    datamodel = SQLAModel(Group, db.session)
    related_views = [ContactGeneralView]


class ContactChartView(ChartView):
    chart_title = 'Grouped contacts'
    label_columns = ContactGeneralView.label_columns
    group_by_columns = ['group', 'gender']
    datamodel = SQLAModel(Contact, db.session)


class ContactTimeChartView(TimeChartView):
    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactGeneralView.label_columns
    group_by_columns = ['birthday']
    datamodel = SQLAModel(Contact, db.session)


fixed_translations_import = [
    _("List Groups"),
    _("List Contacts"),
    _("Contacts Chart"),
    _("Contacts Birth Chart")]


fill_gender()
genapp = BaseApp(app, db)
genapp.add_view(GroupGeneralView(), "List Groups", icon="fa-folder-open-o", category="Contacts")
genapp.add_view(ContactGeneralView(), "List Contacts", icon="fa-envelope", category="Contacts")
genapp.add_separator("Contacts")
genapp.add_view(ContactChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts")
genapp.add_view(ContactTimeChartView(), "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

