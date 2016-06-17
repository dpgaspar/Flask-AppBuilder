import calendar
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.widgets import FormHorizontalWidget, FormInlineWidget, FormVerticalWidget
from flask_babel import lazy_gettext as _


from app import db, appbuilder
from .models import ContactGroup, ContactSubGroup, Gender, Contact



class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    list_columns = ['name', 'contact_group.name', 'contact_sub_group.name']

    base_order = ('name', 'asc')
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group', 'contact_sub_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group', 'contact_sub_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_group', 'contact_sub_group']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    add_form_extra_fields = {
                    'contact_group': AJAXSelectField('contact_group',
                    description='This will be populated with AJAX',
                    datamodel=datamodel,
                    col_name='contact_group',
                    widget=Select2AJAXWidget(endpoint='/contactmodelview/api/column/add/contact_group')),

                    'contact_sub_group': AJAXSelectField('Extra Field2',
                    description='Extra Field description',
                    datamodel=datamodel,
                    col_name='contact_sub_group',
                    widget=Select2SlaveAJAXWidget(master_id='contact_group',
                    endpoint='/contactmodelview/api/column/add/contact_sub_group?_flt_0_contact_group_id={{ID}}'))
                    }

    edit_form_extra_fields = add_form_extra_fields


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class SubGroupModelView(ModelView):
    datamodel = SQLAInterface(ContactSubGroup)
    list_columns = ['name', 'contact_group.name']
    add_columns = ['name', 'contact_group']
    edit_columns = ['name', 'contact_group']
    show_columns = ['name', 'contact_group']
    related_views = [ContactModelView]



db.create_all()
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(SubGroupModelView, "List Sub Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
