from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Role


class RoleApi(ModelRestApi):
    resource_name = "role"
    class_permission_name = "Role"
    datamodel = SQLAInterface(Role)
    allow_browser_login = True

    list_columns = ["id", "permissions", "name"]
    show_columns = list_columns
    add_columns = ["name", "permissions"]
    edit_columns = ["name", "permissions"]
    search_columns = list_columns
