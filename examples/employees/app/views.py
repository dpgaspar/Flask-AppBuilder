from flask import render_template, current_app
from flask.ext.appbuilder.views import ModelView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListBlock, ShowBlockWidget
from .models import Employee,Department, Function

from app import appbuilder, db, app


class EmployeeView(ModelView):
    datamodel = SQLAModel(Employee)

    list_columns = ['employee_number', 'full_name', 'department']
    edit_columns = ['employee_number','full_name','department','begin_date']


class FunctionView(ModelView):
    datamodel = SQLAModel(Function)


class DepartmentView(ModelView):
    datamodel = SQLAModel(Department)


db.create_all()
appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")

