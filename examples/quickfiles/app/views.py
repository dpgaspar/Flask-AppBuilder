from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView, ListAddViewMixin
from app.models import Project, ProjectFiles
from flask.ext.appbuilder import Base
from app import app, db


class ProjectFilesGeneralView(GeneralView, ListAddViewMixin):
    datamodel = SQLAModel(ProjectFiles, db.session)
    
    label_columns = {'download':'Download'}
    add_columns = ['file']
    edit_columns = ['file']
    list_columns = ['file','download']
    show_columns = ['file','download']
    

class ProjectGeneralView(GeneralView):
    datamodel = SQLAModel(Project, db.session)
    related_views = [ProjectFilesGeneralView()]    

    add_columns = ['name']
    edit_columns = ['name']
    list_columns = ['name','created_by', 'created_on', 'changed_by','changed_on']
    show_fieldsets = [
                 ('Info',{'fields':['name']}),
                 ('Audit',{'fields':['created_by', 'created_on', 'changed_by','changed_on'],'expanded':False})
                 ]



baseapp = BaseApp(app, db)
baseapp.add_view(ProjectGeneralView(), "List Projects",icon = "fa-table",category = "Projects")
baseapp.add_view_no_menu(ProjectFilesGeneralView())

