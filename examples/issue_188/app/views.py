from flask import redirect, flash
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.actions import action
from models import Job
from app import appbuilder, db

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

db.create_all()

class JobModelView(ModelView):
    datamodel = SQLAInterface(Job)

    list_columns = ['name','start_time','PAYLOAD']
    #add_columns = ['name', 'PAYLOAD']
    add_columns = []
    show_fieldsets = [
        ('Summary',{'fields':['name','PAYLOAD']}),
        ('Job Info',{'fields':['module_type', 'start_time','SRVHOST','SRVPORT','LHOST','LPORT'],'expanded':False}),
        ]

    @action("job_kill", "Kill", "Kill all selected?", "fa-rocket")
    def kill(self, items):
        if isinstance(items, list):
            for item in items:
                result = "test result"
                flash(str(item.id), "info")
                flash(str(result), "info")
        else:
                result = "test result"
                flash(str(items.id), "info")
                flash(str(result), "info")
        self.update_redirect()
        return redirect(self.get_redirect())

    @action("job_stop", "Stop", "Stop all selected?", "fa-rocket")
    def stop(self, items):
        print "stopping"
        return redirect(self.get_redirect())

appbuilder.add_view(JobModelView, "List Jobs",icon = "fa-folder-open-o",category = "Contacts",
                category_icon = "fa-envelope")
