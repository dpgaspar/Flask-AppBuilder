from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Permission


class PermissionApi(ModelRestApi):
    resource_name = "security/permissions"
    openapi_spec_tag = "Security Permissions"

    class_permission_name = "Permission"
    datamodel = SQLAInterface(Permission)
    allow_browser_login = True
    include_route_methods = {"info", "get", "get_list"}

    list_columns = ["id", "name"]
    show_columns = list_columns
    add_columns = ["name"]
    edit_columns = add_columns
    search_columns = list_columns
