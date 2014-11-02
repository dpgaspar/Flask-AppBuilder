from flask import render_template, current_app, blueprints, redirect, url_for
from flask_appbuilder import expose
from flask.ext.appbuilder.views import ModelView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListBlock, ShowBlockWidget
from .models import Employee,Department, Function

from app import appbuilder, db, app


class EmployeeView(ModelView):
    datamodel = SQLAModel(Employee)

    list_columns = ['employee_number', 'full_name', 'department']


class FunctionView(ModelView):
    datamodel = SQLAModel(Function)


class DepartmentView(ModelView):
    datamodel = SQLAModel(Department)


class ErrorHandlers(BaseView):

    http_404_template = '404.html'

    @expose('/404')
    def http_404(self):
        return self.render_template(self.http_404_template, appbuilder=appbuilder)


@app.errorhandler(404)
def error_handler(e):
    return redirect(url_for('ErrorHandlers.http_404'))


db.create_all()
appbuilder.add_view_no_menu(ErrorHandlers,"ErrorHandlers")
appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")

