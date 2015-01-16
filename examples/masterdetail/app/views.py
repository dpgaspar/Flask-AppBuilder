from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder.views import MasterDetailView
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.charts.views import ChartView, TimeChartView
from flask.ext.babelpkg import lazy_gettext as _

from app import db, appbuilder
from models import ContactGroup, Gender, Contact


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


class ContactGeneralView(ModelView):
    datamodel = SQLAInterface(Contact)

    label_columns = {'contact_grouo': 'Contacts Group'}
    list_columns = ['name', 'personal_phone', 'contact_group']

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
    _("Contacts Birth Chart")]

db.create_all()
fill_gender()
appbuilder.add_view(GroupMasterView, "List Groups", icon="fa-folder-open-o", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(GroupGeneralView, "Manage Groups", icon="fa-folder-open-o", category="Contacts")
appbuilder.add_view(ContactGeneralView, "List Contacts", icon="fa-envelope", category="Contacts")

