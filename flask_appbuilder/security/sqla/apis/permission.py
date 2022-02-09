from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Permission


class PermissionApi(ModelRestApi):
    resource_name = "permission"
    class_permission_name = "Permission"
    datamodel = SQLAInterface(Permission)
    allow_browser_login = True
