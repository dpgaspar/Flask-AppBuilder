import calendar
from flask import redirect
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.models import SQLAInterface
from flask.ext.appbuilder.charts.views import GroupByChartView
from flask.ext.appbuilder.models.group import aggregate_count
from flask.ext.appbuilder.widgets import FormVerticalWidget, FormInlineWidget, FormHorizontalWidget, ShowBlockWidget
from flask.ext.appbuilder.actions import action
from flask_appbuilder.widgets import ListThumbnail
from flask.ext.babelpkg import lazy_gettext as _
from flask.ext.appbuilder.models.generic import PSSession
from flask_appbuilder.models.generic.interface import GenericInterface
from flask_appbuilder.models.generic import PSModel
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction as FA
from flask_appbuilder import expose, has_access, permission_name, BaseView
from flask_appbuilder import IndexView

from app import db, appbuilder
from .models import ContactGroup, Gender, Contact, FloatModel, Product, ProductManufacturer, ProductModel


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


sess = PSSession()


class PSView(ModelView):
    datamodel = GenericInterface(PSModel, sess)
    base_permissions = ['can_list', 'can_show']
    list_columns = ['UID', 'C', 'CMD', 'TIME']
    search_columns = ['UID', 'C', 'CMD']


class ProductManufacturerView(ModelView):
    datamodel = SQLAInterface(ProductManufacturer)


class ProductModelView(ModelView):
    datamodel = SQLAInterface(ProductModel)


class ProductView(ModelView):
    datamodel = SQLAInterface(Product)
    list_columns = ['name','product_manufacturer', 'product_model']
    add_columns = ['name','product_manufacturer', 'product_model']
    edit_columns = ['name','product_manufacturer', 'product_model']
    add_widget = FormVerticalWidget


class ContactModelView2(ModelView):
    datamodel = SQLAInterface(Contact)
    #label_columns = {'contact_groups.name': 'Contacts Group'}
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_groups.name']
    add_form_query_rel_fields = {'contact_groups':[['name',FilterStartsWith,'p']],
                                 'gender':[['name',FilterStartsWith,'F']]}



class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    add_widget = FormVerticalWidget
    show_widget = ShowBlockWidget

    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_groups.name']

    list_template = 'list_contacts.html'
    list_widget = ListThumbnail
    show_template = 'show_contacts.html'

    extra_args = {'extra_arg_obj1': 'Extra argument 1 injected'}
    base_order = ('name', 'asc')

    show_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_groups']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_groups']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'gender', 'contact_groups']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    ]

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    list_columns = ['name', 'extra_col']

class FloatModelView(ModelView):
    datamodel = SQLAInterface(FloatModel)


class ContactChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group': 'contact_groups',
            'series': [(aggregate_count, 'contact_groups')]
        },
        {
            'group': 'gender',
            'series': [(aggregate_count, 'gender')]
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
            'group': 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'contact_groups')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'contact_groups')]
        }
    ]


db.create_all()
fill_gender()

appbuilder.add_view(PSView, "List PS", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts",
                    category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(ContactModelView2, "List Contacts 2", icon="fa-envelope", category="Contacts")
appbuilder.add_view(FloatModelView, "List Float Model", icon="fa-envelope", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

appbuilder.add_view(ProductManufacturerView, "List Manufacturer", icon="fa-folder-open-o", category="Products",
                    category_icon='fa-envelope')
appbuilder.add_view(ProductModelView, "List Models", icon="fa-envelope", category="Products")
appbuilder.add_view(ProductView, "List Products", icon="fa-envelope", category="Products")

appbuilder.security_cleanup()


