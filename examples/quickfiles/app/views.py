from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from app.models import Project, ProjectFiles
from flask.ext.appbuilder import Base
from app import app, db


class ProjectGeneralView(GeneralView):
    datamodel = SQLAModel(Project, db.session)
    related_views = []    

    add_columns = ['name']
    edit_columns = ['name']
    list_columns = ['name','created_by', 'created_on', 'changed_by','changed_on']
    show_columns = ['name','created_by', 'created_on', 'changed_by','changed_on']
    order_columns = ['name']
    search_columns = ['name', 'created_by']
    show_fieldsets = [
                 ('Info',{'fields':['name']}),
                 ('Audit',{'fields':['created_by', 'created_on', 'changed_by','changed_on'],'expanded':False})
                 ]

baseapp = BaseApp(app, db)
baseapp.add_view(ProjectGeneralView(), "List Projects",icon = "th-large",category = "Projects")
print Base.metadata.tables.keys()
