from flask import render_template, current_app, blueprints, redirect, url_for
from flask_appbuilder import expose
from flask.ext.appbuilder.views import ModelView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask_appbuilder.fieldwidgets import Select2Widget
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListBlock, ShowBlockWidget
from .models import Employee,Department, Function, EmployeeHistory
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app import appbuilder, db, app


def department_query():
    return db.session.query(Department)


class Select2ROWidget(Select2Widget):
    def __call__(self, field, **kwargs):
        kwargs['disabled'] = 'true'
        return super(Select2ROWidget, self).__call__(field, **kwargs)


class EmployeeHistoryView(ModelView):
    datamodel = SQLAModel(EmployeeHistory)


class EmployeeView(ModelView):
    datamodel = SQLAModel(Employee)

    list_columns = ['employee_number', 'full_name', 'department']

    edit_form_extra_fields = {'department':  QuerySelectField('Department',
                                query_factory=department_query,
                                widget=Select2ROWidget())}
    related_views = [EmployeeHistoryView]
    show_template = 'appbuilder/general/model/show_cascade.html'


class FunctionView(ModelView):
    datamodel = SQLAModel(Function)


class DepartmentView(ModelView):
    datamodel = SQLAModel(Department)


db.create_all()

appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")

