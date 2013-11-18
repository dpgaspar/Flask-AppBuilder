from flask.ext.appbuilder.menu import Menu
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from flask.ext.appbuilder.charts.views import ChartView

from app import app, db
from models import Group, Contact


class ContactGeneralView(GeneralView):
    route_base = '/contacts'
    datamodel = SQLAModel(Contact, db.session)

    list_title = 'List Contacts'
    show_title = 'Show Contact'
    add_title = 'Add Contact'
    edit_title = 'Edit Contact'

    label_columns = {'name':'Name','photo':'Photo','address':'Address','birthday':'Birthday',
                'personal_phone':'Personal Phone',
                'personal_celphone':'Personal CelPhone', 'group':'Contacts Group'}
    list_columns = ['name','personal_celphone','birthday','group']

    order_columns = ['name','personal_celphone','birthday']
    search_columns = ['name','personal_celphone','group']

    show_fieldsets = [
         ('Summary',{'fields':['name','address','group']}),
         ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
         ]


class GroupGeneralView(GeneralView):
    route_base = '/groups'
    datamodel = SQLAModel(Group, db.session)
    related_views = [ContactGeneralView()]

    list_title = 'List Groups'
    show_title = 'Show Group'
    add_title = 'Add Group'
    edit_title = 'Edit Group'

    label_columns = { 'name':'Name'}
    list_columns = ['name']
    show_columns = ['name']
    order_columns = ['name']
    search_columns = ['name']

class ContactChartView(ChartView):
    
    route_base = '/contacts'
    chart_title = 'Grouped contacts'
    label_columns = ContactGeneralView.label_columns
    group_by_columns = ['group']
    datamodel = SQLAModel(Contact, db.session)



genapp = BaseApp(app)
genapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
genapp.add_view(ContactGeneralView, "List Contacts","/contacts/list","earphone","Contacts")
genapp.add_view(ContactChartView, "Contacts Chart","/contacts/chart","earphone","Contacts")
