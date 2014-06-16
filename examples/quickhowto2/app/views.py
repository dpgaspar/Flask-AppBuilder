from flask import Flask
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import ModelView
from flask.ext.appbuilder.charts.views import ChartView, TimeChartView
from flask.ext.babelpkg import lazy_gettext as _
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, BS3PasswordFieldWidget
from wtforms import TextField, widgets

from app import appbuilder, db
from .models import Group, Gender, Contact


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)


class ContactModelView(ModelView):
    datamodel = SQLAModel(Contact)

    label_columns = {'group': 'Contacts Group'}
    list_columns = ['name', 'personal_celphone', 'birthday', 'group']

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

    edit_form_extra_fields = {'address': TextField('address',
                                        widget=BS3TextFieldROWidget())}


class ContactChartView(ChartView):
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    group_by_columns = ['group', 'gender']
    datamodel = SQLAModel(Contact)


class ContactTimeChartView(TimeChartView):
    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactModelView.label_columns
    group_by_columns = ['birthday']
    datamodel = SQLAModel(Contact)


class GroupModelView(ModelView):
    datamodel = SQLAModel(Group)
    related_views = [ContactModelView]
    #base_permissions = ['can_list']

fixed_translations_import = [
    _("List Groups"),
    _("List Contacts"),
    _("Contacts Chart"),
    _("Contacts Birth Chart")]


appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")


