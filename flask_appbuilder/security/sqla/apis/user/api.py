from datetime import datetime

from flask import g, request
from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import expose, safe
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import permission_name, protect
from flask_appbuilder.security.sqla.apis.user.schema import (
    UserPostSchema,
    UserPutSchema,
)
from flask_appbuilder.security.sqla.models import Role, User
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


class UserApi(ModelRestApi):
    resource_name = "security/users"
    openapi_spec_tag = "Security Users"
    class_permission_name = "User"
    datamodel = SQLAInterface(User)
    allow_browser_login = True

    list_columns = [
        "id",
        "roles.id",
        "roles.name",
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
    ]
    show_columns = list_columns
    add_columns = [
        "roles",
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
        "password",
    ]
    edit_columns = add_columns
    search_columns = [
        "username",
        "first_name",
        "last_name",
        "active",
        "email",
        "created_by",
        "changed_by",
        "roles",
    ]

    add_model_schema = UserPostSchema()
    edit_model_schema = UserPutSchema()

    def pre_update(self, item):
        item.changed_on = datetime.now()
        item.changed_by_fk = g.user.id
        if item.password:
            item.password = generate_password_hash(item.password)

    def pre_add(self, item):
        item.password = generate_password_hash(item.password)

    @expose("/", methods=["POST"])
    @protect()
    @safe
    @permission_name("post")
    def post(self):
        """Create new user
        ---
        post:
          requestBody:
            description: Model schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
          responses:
            201:
              description: Item changed
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
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
                        role = (
                            self.datamodel.session.query(Role)
                            .filter(Role.id == role_id)
                            .one_or_none()
                        )
                        if role:
                            role.user_id = model.id
                            role.role_id = role_id
                            roles.append(role)

            if "roles" in item.keys():
                model.roles = roles

            self.pre_add(model)
            self.datamodel.add(model, raise_exception=True)
            return self.response(201, id=model.id)
        except ValidationError as error:
            return self.response_400(message=error.messages)
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @expose("/<pk>", methods=["PUT"])
    @protect()
    @safe
    @permission_name("put")
    def put(self, pk):
        """Edit user
        ---
        put:
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
          requestBody:
            description: Model schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
          responses:
            200:
              description: Item changed
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.edit_model_schema.load(request.json)
            model = self.datamodel.get(pk, self._base_filters)
            roles = []

            for key, value in item.items():
                if key != "roles":
                    setattr(model, key, value)
                else:
                    for role_id in item[key]:
                        role = (
                            self.datamodel.session.query(Role)
                            .filter(Role.id == role_id)
                            .one_or_none()
                        )
                        if role:
                            role.user_id = model.id
                            role.role_id = role_id
                            roles.append(role)

            if "roles" in item.keys():
                model.roles = roles

            self.pre_update(model)
            self.datamodel.edit(model, raise_exception=True)
            return self.response(
                200,
                **{API_RESULT_RES_KEY: self.edit_model_schema.dump(item, many=False)},
            )

        except ValidationError as e:
            return self.response_400(message=e.messages)
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))
