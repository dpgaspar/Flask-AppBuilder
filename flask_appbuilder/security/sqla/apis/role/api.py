from flask import current_app, request
from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import expose, safe
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import permission_name, protect
from flask_appbuilder.security.sqla.apis.role.schema import (
    RoleGroupPutSchema,
    RolePermissionListSchema,
    RolePermissionPostSchema,
    RoleUserPutSchema,
)
from flask_appbuilder.security.sqla.models import Group, PermissionView, Role, User
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


class RoleApi(ModelRestApi):
    resource_name = "security/roles"
    openapi_spec_tag = "Security Roles"
    class_permission_name = "Role"
    datamodel = SQLAInterface(Role)
    allow_browser_login = True

    list_columns = ["id", "name"]
    show_columns = list_columns
    add_columns = ["name"]
    edit_columns = ["name"]
    search_columns = list_columns

    update_role_group_schema = RoleGroupPutSchema()
    list_role_permission_schema = RolePermissionListSchema()
    add_role_permission_schema = RolePermissionPostSchema()
    update_role_user_schema = RoleUserPutSchema()
    openapi_spec_component_schemas = (
        RolePermissionListSchema,
        RolePermissionPostSchema,
        RoleUserPutSchema,
        RoleGroupPutSchema,
    )

    @expose("/<int:role_id>/permissions/", methods=["GET"])
    @protect()
    @safe
    @permission_name("list_role_permissions")
    def list_role_permissions(self, role_id):
        """list role permissions
        ---
        get:
          parameters:
          - in: path
            schema:
              type: integer
            name: role_id
          responses:
            200:
              description: List of permissions
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/RolePermissionListSchema'
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
        role = self.datamodel.get(role_id, select_columns=["permissions"])
        if not role:
            return self.response_404()

        permissions = [
            {
                "id": p.id,
                "permission_name": p.permission.name,
                "view_menu_name": p.view_menu.name,
            }
            for p in role.permissions
        ]
        return self.response(200, **{API_RESULT_RES_KEY: permissions})

    @expose("/<int:role_id>/permissions", methods=["POST"])
    @protect()
    @safe
    @permission_name("add_role_permissions")
    def add_role_permissions(self, role_id):
        """add role permissions
        ---
        post:
          parameters:
          - in: path
            schema:
              type: integer
            name: role_id
          requestBody:
            description: Add role permissions schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/RolePermissionPostSchema'
          responses:
            200:
              description: Permissions added
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/RolePermissionPostSchema'
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
            item = self.add_role_permission_schema.load(request.json)
            role = self.datamodel.get(role_id)
            if not role:
                return self.response_404()
            permissions = []
            for id in item["permission_view_menu_ids"]:
                permission = (
                    current_app.appbuilder.get_session.query(PermissionView)
                    .filter_by(id=id)
                    .one_or_none()
                )
                if permission:
                    permissions.append(permission)

            role.permissions = permissions
            self.datamodel.edit(role, raise_exception=True)
            return self.response(
                200,
                **{
                    API_RESULT_RES_KEY: self.add_role_permission_schema.dump(
                        item, many=False
                    )
                },
            )

        except ValidationError as error:
            return self.response_400(message=error.messages)
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @expose("/<int:role_id>/users", methods=["PUT"])
    @protect()
    @safe
    @permission_name("update_role_users")
    def update_role_users(self, role_id):
        """update role users
        ---
        put:
          parameters:
          - in: path
            schema:
              type: integer
            name: role_id
          requestBody:
            description: Update role users schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/RoleUserPutSchema'
          responses:
            200:
              description: Role users updated
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/RoleUserPutSchema'
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
            item = self.update_role_user_schema.load(request.json)
            role = self.datamodel.get(role_id)
            if not role:
                return self.response_404()

            users = (
                current_app.appbuilder.get_session.query(User)
                .filter(User.id.in_(item["user_ids"]))
                .all()
            )

            if len(users) != len(item["user_ids"]):
                return self.response_404()  # Some users were not found

            role.user = users
            self.datamodel.edit(role, raise_exception=True)
            return self.response(
                200,
                **{
                    API_RESULT_RES_KEY: self.update_role_user_schema.dump(
                        item, many=False
                    )
                },
            )

        except ValidationError as error:
            return self.response_400(message=error.messages)
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @expose("/<int:role_id>/groups", methods=["PUT"])
    @protect()
    @safe
    @permission_name("update_role_groups")
    def update_role_groups(self, role_id):
        """Update role groups
        ---
        put:
          parameters:
          - in: path
            schema:
              type: integer
            name: role_id
          requestBody:
            description: Update role groups schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/RoleGroupPutSchema'
          responses:
            200:
              description: Role groups updated
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/RoleGroupPutSchema'
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
            item = self.update_role_group_schema.load(request.json)
            role = self.datamodel.get(role_id)
            if not role:
                return self.response_404()

            groups = (
                current_app.appbuilder.get_session.query(Group)
                .filter(Group.id.in_(item["group_ids"]))
                .all()
            )

            if len(groups) != len(item["group_ids"]):
                return self.response_404()  # Some groups were not found

            role.groups = groups
            self.datamodel.edit(role, raise_exception=True)
            return self.response(
                200,
                **{
                    API_RESULT_RES_KEY: self.update_role_group_schema.dump(
                        item, many=False
                    )
                },
            )

        except ValidationError as error:
            return self.response_400(message=error.messages)
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))
