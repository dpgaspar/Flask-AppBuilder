from flask_appbuilder import ModelView
from flask_appbuilder.extensions import db
from flask_appbuilder.fields import QuerySelectField
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import Benefit, Department, Employee, EmployeeHistory, Function


def department_query():
    return db.session.query(Department)


class EmployeeHistoryView(ModelView):
    datamodel = SQLAInterface(EmployeeHistory)
    # base_permissions = ['can_add', 'can_show']
    list_columns = ["department", "begin_date", "end_date"]


class EmployeeView(ModelView):
    datamodel = SQLAInterface(Employee)

    list_columns = ["full_name", "department.name", "employee_number"]
    edit_form_extra_fields = {
        "department": QuerySelectField(
            "Department",
            query_func=department_query,
            widget=Select2Widget(extra_classes="readonly"),
        )
    }

    related_views = [EmployeeHistoryView]
    show_template = "appbuilder/general/model/show_cascade.html"


class FunctionView(ModelView):
    datamodel = SQLAInterface(Function)
    related_views = [EmployeeView]


class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeView]


class BenefitView(ModelView):
    datamodel = SQLAInterface(Benefit)
    add_columns = ["name"]
    edit_columns = ["name"]
    show_columns = ["name"]
    list_columns = ["name"]
