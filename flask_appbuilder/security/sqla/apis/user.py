from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import User

class UserApi(ModelRestApi):
    resource_name = "user"
    class_permission_name = "User"
    datamodel = SQLAInterface(User)
    allow_browser_login = True

    list_columns = [
        "roles",
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
        "last_login",
        "login_count",
        "fail_login_count",
        "created_on",
        "changed_on",
        "created_by.id",
        "changed_by.id",
        "created.id",
        "changed.id"
    ]
    show_columns = list_columns
    add_columns = [
        "roles",
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
    ]
    edit_columns = add_columns
    search_columns = list_columns
