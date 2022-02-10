from datetime import datetime
from flask import g, request
from flask_appbuilder import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import User, Role
from werkzeug.security import generate_password_hash
from .schema import UserPostSchema
from marshmallow import ValidationError
from flask_appbuilder.api import expose
from flask import current_app

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
        "changed.id",
    ]
    show_columns = list_columns
    add_columns = ["roles", "first_name", "last_name", "username", "active", "email", "password"]
    edit_columns = add_columns
    search_columns = list_columns

    add_model_schema = UserPostSchema()
 
    def pre_update(self, item):
        """
            Override this, will be called after update
        """
        item.changed_on = datetime.now()
        item.changed_by_fk = g.user.id
        item.password = generate_password_hash(item.password)

    def pre_add(self, item):
        """
            Override this, will be called after update
        """
        item.password = generate_password_hash(item.password)

    @expose("/", methods=["POST"])
    def post(self):
        """Create new user
        """
        try:
            item = self.add_model_schema.load(request.json)
            model = User()
            roles = []
            for key, value in item.items():
                if key != "roles":
                    setattr(model, key, value)
                else:
                    for role_id in item[key]:
                        role = current_app.appbuilder.session.query(Role).filter(Role.id == role_id).first()
                        role.user_id = model.id
                        role.role_id = role_id
                        roles.append(role)
                    model.roles = roles
            self.pre_add(model)
            self.datamodel.add(model, raise_exception=True)
        except ValidationError as error:
            return self.response_400(message=error.messages)
        return self.response(201, id = model.id, result=item)

