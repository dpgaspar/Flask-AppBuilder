from flask_appbuilder import ModelView
from flask_appbuilder.fieldwidgets import Select2Widget
from flask.ext.appbuilder.models.datamodel import SQLAModel
from .models import Employee,Department, Function, EmployeeHistory, Benefit
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app import appbuilder, db


def department_query():
    return db.session.query(Department)


class Select2ROWidget(Select2Widget):
    def __call__(self, field, **kwargs):
        kwargs['disabled'] = 'true'
        return super(Select2ROWidget, self).__call__(field, **kwargs)


class EmployeeHistoryView(ModelView):
    datamodel = SQLAModel(EmployeeHistory)
    #base_permissions = ['can_add', 'can_show']
    list_columns = ['department', 'begin_date', 'end_date']

    def pre_add(self, item):
        prev_item = db.session.query(EmployeeHistory).filter(EmployeeHistory.end_date==None).scalar()
        if prev_item:
            prev_item.end_date = item.begin_date
            db.session.merge(prev_item)
            db.session.commit()

    def post_add(self, item):
        empployee = db.session.query(Employee).get(item.employee_id)
        empployee.department = item.department
        db.session.merge(empployee)
        db.session.commit()


class EmployeeView(ModelView):
    datamodel = SQLAModel(Employee)

    list_columns = ['full_name', 'department', 'employee_number']

    edit_form_extra_fields = {'department':  QuerySelectField('Department',
                                query_factory=department_query,
                                widget=Select2ROWidget())}
    related_views = [EmployeeHistoryView]
    show_template = 'appbuilder/general/model/show_cascade.html'

    def post_add(self, item):
        employee_history = EmployeeHistory()
        employee_history.employee_id = item.id
        employee_history.department = item.department
        employee_history.begin_date = item.begin_date
        db.session.add(employee_history)
        db.session.commit()


class FunctionView(ModelView):
    datamodel = SQLAModel(Function)
    related_views = [EmployeeView]


class DepartmentView(ModelView):
    datamodel = SQLAModel(Department)
    related_views = [EmployeeView]


class BenefitView(ModelView):
    datamodel = SQLAModel(Benefit)
    related_views = [EmployeeView]
    add_columns = ['name']
    edit_columns = ['name']
    show_columns = ['name']
    list_columns = ['name']


db.create_all()

appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(BenefitView, "Benefits", icon="fa-folder-open-o", category="Company")

