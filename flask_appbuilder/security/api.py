from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity
from flask_babel import lazy_gettext
from ..const import (
    API_SECURITY_VERSION,
    API_SECURITY_PROVIDER_DB,
    API_SECURITY_PROVIDER_LDAP,
    API_SECURITY_USERNAME_KEY,
    API_SECURITY_PASSWORD_KEY,
    API_SECURITY_PROVIDER_KEY,
    API_SECURITY_REFRESH_KEY,
    API_SECURITY_ACCESS_TOKEN_KEY,
    API_SECURITY_REFRESH_TOKEN_KEY
)
from ..views import expose
from ..api import BaseApi, ModelRestApi, safe


class SecurityApi(BaseApi):

    resource_name = 'security'
    version = API_SECURITY_VERSION

    @expose('/login', methods=['POST'])
    @safe
    def login(self):
        """
            Login endpoint for the API returns a JWT and possibly a refresh token
        :return: Flask response with JSON payload containing an
            access_token and refresh_token
        """
        if not request.is_json:
            return self.response_400(message="Request payload is not JSON")
        username = request.json.get(API_SECURITY_USERNAME_KEY, None)
        password = request.json.get(API_SECURITY_PASSWORD_KEY, None)
        provider = request.json.get(API_SECURITY_PROVIDER_KEY, None)
        refresh = request.json.get(API_SECURITY_REFRESH_KEY, False)
        if not username or not password or not provider:
            return self.response_400(message="Missing required parameter")
        # AUTH
        if provider == API_SECURITY_PROVIDER_DB:
            user = self.appbuilder.sm.auth_user_db(
                username,
                password
            )
        elif provider == API_SECURITY_PROVIDER_LDAP:
            user = self.appbuilder.sm.auth_user_ldap(
                username,
                password
            )
        else:
            return self.response_400(
                message="Provider {} not supported".format(provider)
            )
        if not user:
            return self.response_401()

        # Identity can be any data that is json serializable
        resp = dict()
        resp[API_SECURITY_ACCESS_TOKEN_KEY] = \
            create_access_token(identity=user.id, fresh=True)
        if refresh:
            resp[API_SECURITY_REFRESH_TOKEN_KEY] = \
                create_refresh_token(identity=user.id)
        return self.response(200, **resp)

    @expose('/refresh', methods=['POST'])
    @jwt_refresh_token_required
    @safe
    def refresh(self):
        """
            Security endpoint for the refresh token, so we can obtain a new
            token without forcing the user to login again
        :return: Flask Response with JSON payload containing
            a new access_token
        """
        resp = {
            API_SECURITY_REFRESH_TOKEN_KEY: create_access_token(
                identity=get_jwt_identity(), fresh=False
            )
        }
        return self.response(200, **resp)
