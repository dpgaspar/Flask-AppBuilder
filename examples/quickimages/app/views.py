from models import Person, PersonGroup
from flask.ext.appbuilder.views import ModelView, BaseView
from flask.ext.appbuilder.charts.views import GroupByChartView
from flask.ext.appbuilder.models.group import aggregate_count
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListThumbnail

from app import app, db, appbuilder


class PersonModelView(ModelView):
    datamodel = SQLAModel(Person, db.session)

    list_title = 'List Contacts'
    show_title = 'Show Contact'
    add_title = 'Add Contact'
    edit_title = 'Edit Contact'

    list_widget = ListThumbnail

    label_columns = {'name': 'Name', 'photo': 'Photo', 'photo_img': 'Photo', 'address': 'Address',
                     'birthday': 'Birthday', 'personal_phone': 'Personal Phone',
                     'personal_celphone': 'Personal Celphone', 'personal_email': 'Personal Email',
                     'business_function': 'Business Function',
                     'business_phone': 'Business Phone', 'business_celphone': 'Business Celphone',
                     'business_email': 'Business Email', 'notes': 'Notes', 'person_group': 'Group', 'person_group_id': 'Group'}
    list_columns = ['photo_img', 'name', 'personal_celphone', 'business_celphone', 'birthday', 'person_group']

    show_fieldsets = [
        ('Summary', {'fields': ['photo_img', 'name', 'address', 'person_group']}),
        ('Personal Info',
         {'fields': ['birthday', 'personal_phone', 'personal_celphone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_phone', 'business_celphone', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'photo', 'address', 'person_group']}),
        ('Personal Info',
         {'fields': ['birthday', 'personal_phone', 'personal_celphone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_phone', 'business_celphone', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'photo', 'address', 'person_group']}),
        ('Personal Info',
         {'fields': ['birthday', 'personal_phone', 'personal_celphone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_phone', 'business_celphone', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]


class GroupModelView(ModelView):
    datamodel = SQLAModel(PersonGroup, db.session)
    related_views = [PersonModelView]

    label_columns = {'phone1': 'Phone (1)', 'phone2': 'Phone (2)', 'taxid': 'Tax ID'}
    list_columns = ['name', 'notes']


class PersonChartView(GroupByChartView):
    datamodel = SQLAModel(Person)
    chart_title = 'Grouped Persons'
    label_columns = PersonModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group': 'person_group',
            'series': [(aggregate_count,'person_group')]
        }
    ]


db.create_all()
appbuilder.add_view(GroupModelView(), "List Groups", icon="fa-folder-open-o", category="Contacts")
appbuilder.add_view(PersonModelView(), "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(PersonChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts")
