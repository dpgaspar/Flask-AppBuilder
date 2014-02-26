from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView, CompactCRUDMixin
from app.models import Project, ProjectFiles
from flask.ext.appbuilder import Base
from app import app, db


class ProjectFilesGeneralView(GeneralView):
    datamodel = SQLAModel(ProjectFiles, db.session)

    label_columns = {'file_name': 'File Name', 'download': 'Download'}
    add_columns = ['file', 'description','project']
    edit_columns = ['file', 'description','project']
    list_columns = ['file_name', 'download']
    show_columns = ['file_name', 'download']


class ProjectGeneralView(CompactCRUDMixin, GeneralView):
    datamodel = SQLAModel(Project, db.session)
    related_views = [ProjectFilesGeneralView]

    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'

    add_columns = ['name']
    edit_columns = ['name']
    list_columns = ['name', 'created_by', 'created_on', 'changed_by', 'changed_on']
    show_fieldsets = [
        ('Info', {'fields': ['name']}),
        ('Audit', {'fields': ['created_by', 'created_on', 'changed_by', 'changed_on'], 'expanded': False})
    ]


baseapp = BaseApp(app, db)
baseapp.add_view(ProjectGeneralView(), "List Projects", icon="fa-table", category="Projects")
baseapp.add_view_no_menu(ProjectFilesGeneralView())
