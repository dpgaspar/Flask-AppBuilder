from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from app.models import Project, ProjectFiles
from app import app, db


class ProjectGeneralView(GeneralView):
    datamodel = SQLAModel(Project, db.session)
    related_views = []    

    list_columns = ['name','created_by', 'created_on', 'changed_by','changed_on']
    show_columns = ['name','created_by', 'created_on', 'changed_by','changed_on']
    order_columns = ['name']
    search_columns = ['name', 'created_by']

baseapp = BaseApp(app, db)
baseapp.add_view(ProjectGeneralView(), "List Projects",icon = "th-large",category = "Projects")
