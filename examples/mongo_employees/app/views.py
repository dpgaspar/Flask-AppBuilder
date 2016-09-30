from fab.flask_appbuilder import ModelView
from fab.flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from .models import Employee, Department, Function, EmployeeHistory, Benefit


def department_query():
    return Department.objects


class EmployeeHistoryView(ModelView):
    datamodel = MongoEngineInterface(EmployeeHistory)
    # base_permissions = ['can_add', 'can_show']
    list_columns = ['department', 'begin_date', 'end_date']


class EmployeeView(ModelView):
    datamodel = MongoEngineInterface(Employee)
    print(datamodel.custom_search)
    list_columns = ['full_name', 'department.name', 'function.name', 'employee_number', 'etags']
    show_template = 'appbuilder/general/model/show_cascade.html'


class FunctionView(ModelView):
    datamodel = MongoEngineInterface(Function)


class DepartmentView(ModelView):
    datamodel = MongoEngineInterface(Department)


class BenefitView(ModelView):
    datamodel = MongoEngineInterface(Benefit)
    custom_search = {'grantees': ('is_list', 'full_name')}

    add_columns = ['name']
    edit_columns = ['name', 'grantees']
    show_columns = ['name']
    list_columns = ['name']


# -------------------------------
# Avoid errors due to class definition loops

def to_avoid_definition_loops():
    # many to many Employee <-> Benefit
    EmployeeView.related_views = [EmployeeHistoryView, BenefitView]
    BenefitView.related_views = [EmployeeView]

    # One to many Function or Department -> Employee
    FunctionView.related_views = [EmployeeView]
    DepartmentView.related_views = [EmployeeView]


to_avoid_definition_loops()


# -------------------------------
# Add the views to the Fab app
def add_views(appbuilder):
    appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
    appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
    appbuilder.add_separator("Company")
    appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
    appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")
    appbuilder.add_view(BenefitView, "Benefits", icon="fa-folder-open-o", category="Company")

    appbuilder.security_cleanup()
