from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Permission


class PermissionApi(ModelRestApi):
    resource_name = "permission"
    class_permission_name = "Permission"
    datamodel = SQLAInterface(Permission)
    allow_browser_login = True

    list_columns = ["id", "name"]
    show_columns = list_columns
    add_columns = ["name"]
    edit_columns = add_columns
    search_columns = list_columns
