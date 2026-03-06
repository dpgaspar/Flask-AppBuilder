from flask import current_app, request
from flask_appbuilder.api import BaseApi, expose, safe
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.security.decorators import permission_name, protect
from flask_appbuilder.security.sqla.apis.api_key.schema import (
    ApiKeyCreateResponseSchema,
    ApiKeyPostSchema,
    ApiKeyResponseSchema,
)
from marshmallow import ValidationError


class ApiKeyApi(BaseApi):
    resource_name = "security/api_keys"
    openapi_spec_tag = "Security API Keys"
    class_permission_name = "ApiKey"
    allow_browser_login = True

    post_schema = ApiKeyPostSchema()
    response_schema = ApiKeyResponseSchema()
    create_response_schema = ApiKeyCreateResponseSchema()
    openapi_spec_component_schemas = (
        ApiKeyPostSchema,
        ApiKeyResponseSchema,
        ApiKeyCreateResponseSchema,
    )

    @expose("/", methods=["GET"])
    @protect()
    @safe
    @permission_name("list")
    def list_api_keys(self):
        """List current user's API keys
        ---
        get:
          responses:
            200:
              description: List of API keys for the current user
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        items:
                          $ref: '#/components/schemas/ApiKeyResponseSchema'
                        type: array
            401:
              $ref: '#/components/responses/401'
            500:
              $ref: '#/components/responses/500'
        """
        sm = current_app.appbuilder.sm
        user = sm.current_user
        api_keys = sm.find_api_keys_for_user(user.id)
        result = self.response_schema.dump(api_keys, many=True)
        return self.response(200, **{API_RESULT_RES_KEY: result})

    @expose("/", methods=["POST"])
    @protect()
    @safe
    @permission_name("create")
    def create_api_key(self):
        """Create a new API key
        ---
        post:
          requestBody:
            description: API key creation parameters
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/ApiKeyPostSchema'
          responses:
            201:
              description: API key created successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/ApiKeyCreateResponseSchema'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.post_schema.load(request.json)
        except ValidationError as error:
            return self.response_400(message=error.messages)

        sm = current_app.appbuilder.sm
        user = sm.current_user
        result = sm.create_api_key(
            user=user,
            name=item["name"],
            scopes=item.get("scopes"),
            expires_on=item.get("expires_on"),
        )
        return self.response(
            201,
            **{API_RESULT_RES_KEY: self.create_response_schema.dump(result)},
        )

    @expose("/<string:key_uuid>", methods=["GET"])
    @protect()
    @safe
    @permission_name("get")
    def get_api_key(self, key_uuid):
        """Get a single API key info
        ---
        get:
          parameters:
          - in: path
            schema:
              type: string
            name: key_uuid
          responses:
            200:
              description: API key details
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/ApiKeyResponseSchema'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        sm = current_app.appbuilder.sm
        api_key = sm.get_api_key_by_uuid(key_uuid)
        user = sm.current_user
        if not api_key or api_key.user_id != user.id:
            return self.response_404()
        result = self.response_schema.dump(api_key)
        return self.response(200, **{API_RESULT_RES_KEY: result})

    @expose("/<string:key_uuid>", methods=["DELETE"])
    @protect()
    @safe
    @permission_name("revoke")
    def revoke_api_key(self, key_uuid):
        """Revoke an API key
        ---
        delete:
          parameters:
          - in: path
            schema:
              type: string
            name: key_uuid
          responses:
            200:
              description: API key revoked
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        sm = current_app.appbuilder.sm
        api_key = sm.get_api_key_by_uuid(key_uuid)
        user = sm.current_user
        if not api_key or api_key.user_id != user.id:
            return self.response_404()

        sm.revoke_api_key(key_uuid)
        return self.response(200, message="API key revoked")
