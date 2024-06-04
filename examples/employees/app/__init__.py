import logging

from flask import Flask
from .security import MySecurityManager
from .views import (
    DepartmentView,
    EmployeeView,
    FunctionView,
    EmployeeHistoryView,
    BenefitView,
)
from .extensions import appbuilder


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)

        appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
        appbuilder.add_view(
            EmployeeView, "Employees", icon="fa-folder-open-o", category="Company"
        )
        appbuilder.add_separator("Company")
        appbuilder.add_view(
            DepartmentView, "Departments", icon="fa-folder-open-o", category="Company"
        )
        appbuilder.add_view(
            FunctionView, "Functions", icon="fa-folder-open-o", category="Company"
        )
        appbuilder.add_view(
            BenefitView, "Benefits", icon="fa-folder-open-o", category="Company"
        )

    return app
