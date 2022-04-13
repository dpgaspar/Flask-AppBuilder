from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import ViewMenu


class ViewMenuApi(ModelRestApi):
    resource_name = "security/resources"
    openapi_spec_tag = "Security Resources (View Menus)"

    class_permission_name = "ViewMenu"
    datamodel = SQLAInterface(ViewMenu)
    allow_browser_login = True

    list_columns = ["id", "name"]
    show_columns = list_columns
    add_columns = ["name"]
    edit_columns = add_columns
    search_columns = list_columns
