from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import PermissionView


class PermissionViewMenuApi(ModelRestApi):
    resource_name = "permissionviewmenu"
    class_permission_name = "PermissionViewMenu"
    datamodel = SQLAInterface(PermissionView)
    allow_browser_login = True

    list_columns = ["id", "permission_id", "view_menu_id"]
    show_columns = list_columns
    add_columns = ["permission_id", "view_menu_id"]
    edit_columns = list_columns
    search_columns = list_columns
