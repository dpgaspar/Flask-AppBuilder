from flask import request
from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import expose, safe
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import permission_name, protect
from flask_appbuilder.security.sqla.apis.group.schema import (
    GroupPostSchema,
    GroupPutSchema,
)
from flask_appbuilder.security.sqla.models import Group, Role, User
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


class GroupApi(ModelRestApi):
    resource_name = "security/groups"
    openapi_spec_tag = "Security Groups"
    class_permission_name = "Group"
    datamodel = SQLAInterface(Group)
    allow_browser_login = True

    list_columns = [
        "id",
        "name",
        "label",
        "description",
        "roles.name",
        "roles.id",
        "users.id",
        "users.username",
    ]
    show_columns = list_columns
    edit_columns = ["name", "label", "description", "users", "roles"]
    add_columns = edit_columns
    search_columns = list_columns

    add_model_schema = GroupPostSchema()
    edit_model_schema = GroupPutSchema()

    openapi_spec_component_schemas = (
        GroupPostSchema,
        GroupPutSchema,
    )

    @expose("/", methods=["POST"])
    @protect()
    @safe
    @permission_name("post")
    def post(self):
        """Create new group
        ---
        post:
          requestBody:
            description: Model schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/GroupPostSchema'
          responses:
            201:
              description: Group created
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/GroupPostSchema'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.add_model_schema.load(request.json)
            model = Group()
            roles = []
            users = []

            for key, value in item.items():
                if key == "roles":
                    roles = self._fetch_entities(Role, value)
                    missing_role_ids = set(item["roles"]) - {r.id for r in roles}
                    if missing_role_ids:
                        return self.response_400(
                            message={
                                "roles": [
                                    (
                                        f"Role(s) with ID(s) {sorted(missing_role_ids)} "
                                        "do not exist."
                                    )
                                ]
                            }
                        )
                elif key == "users":
                    users = self._fetch_entities(User, value)
                    missing_user_ids = set(item["users"]) - {u.id for u in users}
                    if missing_user_ids:
                        return self.response_400(
                            message={
                                "users": [
                                    (
                                        f"User(s) with ID(s) {sorted(missing_user_ids)} "
                                        "do not exist."
                                    )
                                ]
                            }
                        )
                else:
                    setattr(model, key, value)

            model.roles = roles
            model.users = users

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
        """Edit group
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
                  $ref: '#/components/schemas/GroupPutSchema'
          responses:
            200:
              description: Group updated
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/GroupPutSchema'
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
            if not model:
                return self.response_404()

            roles = []
            users = []

            for key, value in item.items():
                if key == "roles":
                    roles = self._fetch_entities(Role, value)
                    missing_role_ids = set(value) - {r.id for r in roles}
                    if missing_role_ids:
                        return self.response_400(
                            message={
                                "roles": [
                                    (
                                        f"Role(s) with ID(s) {sorted(missing_role_ids)} "
                                        "do not exist."
                                    )
                                ]
                            }
                        )
                elif key == "users":
                    users = self._fetch_entities(User, value)
                    missing_user_ids = set(value) - {u.id for u in users}
                    if missing_user_ids:
                        return self.response_400(
                            message={
                                "users": [
                                    (
                                        f"User(s) with ID(s) {sorted(missing_user_ids)} "
                                        "do not exist."
                                    )
                                ]
                            }
                        )
                else:
                    setattr(model, key, value)

            if "roles" in item.keys():
                model.roles = roles
            if "users" in item.keys():
                model.users = users
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
