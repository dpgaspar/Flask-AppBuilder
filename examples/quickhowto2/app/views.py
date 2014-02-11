from flask.ext.appbuilder.menu import Menu
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from flask.ext.appbuilder.charts.views import ChartView, TimeChartView
from flask.ext.babelpkg import lazy_gettext as _

from app import app, db
from models import Group, Gender, Contact

def fill_gender():
    g1 = Gender()
    g1.name = 'Male'
    g2 = Gender()
    g2.name = 'Female'
    try:
        db.session.add(g1)
        db.session.add(g2)
        db.session.commit()
    except:
        db.session.rollback()

class ContactGeneralView(GeneralView):
    datamodel = SQLAModel(Contact, db.session)

    label_columns = {'group':'Contacts Group'}
    list_columns = ['name','personal_celphone','birthday','group']

    base_order = ('name','asc')

    show_fieldsets = [
         ('Summary',{'fields':['name','gender','address','group']}),
         ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
         ]


class GroupGeneralView(GeneralView):
    datamodel = SQLAModel(Group, db.session)
    related_views = [ContactGeneralView]

class ContactChartView(ChartView):
    chart_title = 'Grouped contacts'
    label_columns = ContactGeneralView.label_columns
    group_by_columns = ['group','gender']
    datamodel = SQLAModel(Contact, db.session)

class ContactTimeChartView(TimeChartView):
    chart_title = 'Grouped Birth contacts'
    label_columns = ContactGeneralView.label_columns
    group_by_columns = ['birthday']
    datamodel = SQLAModel(Contact, db.session)




fixed_translations_import = [
        _("List Groups"),
        _("List Contacts"),
        _("Contacts Chart"),
        _("Contacts Birth Chart")]
        
genapp = BaseApp(app, db)
genapp.add_view(GroupGeneralView(), "List Groups",icon = "fa-folder-open-o",category = "Contacts")
genapp.add_view(ContactGeneralView(), "List Contacts",icon = "fa-envelope",category = "Contacts")
genapp.add_separator("Contacts")
genapp.add_view(ContactChartView(), "Contacts Chart","/contactchartview/chart","fa-dashboard","Contacts")
genapp.add_view(ContactTimeChartView(), "Contacts Birth Chart","/contacttimechartview/chart/month","fa-dashboard","Contacts")

