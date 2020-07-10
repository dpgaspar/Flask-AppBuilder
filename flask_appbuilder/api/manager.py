from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import current_app
from flask_appbuilder.api import BaseApi
from flask_appbuilder.api import expose, protect, safe
from flask_appbuilder.basemanager import BaseManager
from flask_appbuilder.baseviews import BaseView
from flask_appbuilder.security.decorators import has_access


class OpenApi(BaseApi):
    route_base = "/api"
    allow_browser_login = True

    @expose("/<version>/_openapi")
    @protect()
    @safe
    def get(self, version):
        """ Endpoint that renders an OpenApi spec for all views that belong
            to a certain version
        ---
        get:
          description: >-
            Get the OpenAPI spec for a specific API version
          parameters:
          - in: path
            schema:
              type: string
            name: version
          responses:
            200:
              description: The OpenAPI spec
              content:
                application/json:
                  schema:
                    type: object
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        version_found = False
        api_spec = self._create_api_spec(version)
        for base_api in current_app.appbuilder.baseviews:
            if isinstance(base_api, BaseApi) and base_api.version == version:
                base_api.add_api_spec(api_spec)
                version_found = True
        if version_found:
            return self.response(200, **api_spec.to_dict())
        else:
            return self.response_404()

    @staticmethod
    def _create_api_spec(version):
        return APISpec(
            title=current_app.appbuilder.app_name,
            version=version,
            openapi_version="3.0.2",
            info=dict(description=current_app.appbuilder.app_name),
            plugins=[MarshmallowPlugin()],
            servers=[{"url": "/api/{}".format(version)}],
        )


class SwaggerView(BaseView):

    route_base = "/swagger"
    default_view = "ui"
    openapi_uri = "/api/{}/_openapi"

    @expose("/<version>")
    @has_access
    def show(self, version):
        return self.render_template(
            "appbuilder/swagger/swagger.html",
            openapi_uri=self.openapi_uri.format(version),
        )


class OpenApiManager(BaseManager):
    def register_views(self):
        if not self.appbuilder.app.config.get("FAB_ADD_SECURITY_VIEWS", True):
            return
        if self.appbuilder.get_app.config.get("FAB_API_SWAGGER_UI", False):
            self.appbuilder.add_api(OpenApi)
            self.appbuilder.add_view_no_menu(SwaggerView)
