from models import Person, Group
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.views import GeneralView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListThumbnail



class PersonGeneralView(GeneralView):
    route_base = '/persons'
    datamodel = SQLAModel(Person, db.session)

    list_title = 'List Contacts'
    show_title = 'Show Contact'
    add_title = 'Add Contact'
    edit_title = 'Edit Contact'
    
    list_widget = ListThumbnail

    label_columns = {'name':'Name','photo':'Photo','photo_img':'Photo','address':'Address','birthday':'Birthday','personal_phone':'Personal Phone',
                'personal_celphone':'Personal Celphone','personal_email':'Personal Email',
                'business_function':'Business Function',
        'business_phone':'Business Phone','business_celphone':'Business Celphone',
                'business_email':'Business Email','notes':'Notes','group':'Group', 'group_id':'Group'}
    list_columns = ['photo_img', 'name','personal_celphone','business_celphone','birthday','group']

    order_columns = ['name','personal_celphone','business_celphone','birthday']
    search_columns = ['name','personal_celphone','group']

    show_fieldsets = [
                 ('Summary',{'fields':['photo_img','name','address','group']}),
                 ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone','personal_email'],'expanded':False}),
                 ('Professional Info',{'fields':['business_function','business_phone','business_celphone','business_email'],'expanded':False}),
                 ('Extra',{'fields':['notes'],'expanded':False}),
                 ]

    add_fieldsets = [
                 ('Summary',{'fields':['name','photo','address','group']}),
                 ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone','personal_email'],'expanded':False}),
                 ('Professional Info',{'fields':['business_function','business_phone','business_celphone','business_email'],'expanded':False}),
                 ('Extra',{'fields':['notes'],'expanded':False}),
                 ]

    edit_fieldsets = [
                 ('Summary',{'fields':['name','photo','address', 'group']}),
                 ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone','personal_email'],'expanded':False}),
                 ('Professional Info',{'fields':['business_function','business_phone','business_celphone','business_email'],'expanded':False}),
                 ('Extra',{'fields':['notes'],'expanded':False}),
                 ]


class GroupGeneralView(GeneralView):
    route_base = '/groups'
    datamodel = SQLAModel(Group, db.session)
    related_views = [PersonGeneralView()]

    list_title = 'List Groups'
    show_title = 'Show Group'
    add_title = 'Add Group'
    edit_title = 'Edit Group'

    label_columns = { 'name':'Name','address':'Address','phone1':'Phone (1)','phone2':'Phone (2)','taxid':'Tax ID','notes':'Notes'}
    list_columns = ['name','notes']
    show_columns = ['name','address','phone1','phone2','taxid','notes']
    order_columns = ['name','notes']
    search_columns = ['name']

class PersonChartView(ChartView):
    
    route_base = '/persons'
    chart_title = 'Grouped Persons'
    label_columns = PersonGeneralView.label_columns
    group_by_columns = ['group']
    datamodel = SQLAModel(Person, db.session)

baseapp = BaseApp(app)
baseapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
baseapp.add_view(PersonGeneralView, "List Contacts","/persons/list","earphone","Contacts")
baseapp.add_view(PersonChartView, "Contacts Chart","/persons/chart","earphone","Contacts")
