from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity
from flask_babel import lazy_gettext
from ..views import expose
from ..api import BaseApi, ModelRestApi, safe


class SecurityApi(BaseApi):

    route_base = '/api/v1/security'

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
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        provider = request.json.get('provider', None)
        refresh = request.json.get('refresh', False)
        if not username or not password or not provider:
            return self.response_400(message="Missing required parameter")
        # AUTH
        if provider == 'db':
            user = self.appbuilder.sm.auth_user_db(
                username,
                password
            )
        elif provider == 'ldap':
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
        resp['access_token'] = create_access_token(identity=user.id, fresh=True)
        if refresh:
            resp['refresh_token'] = create_refresh_token(identity=user.id)
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
        return self.response(
            200,
            access_token=create_access_token(identity=get_jwt_identity(), fresh=False)
        )


class UserApi(ModelRestApi):
    resource_name = 'user'

    label_columns = {
        'get_full_name': lazy_gettext('Full Name'),
        'first_name': lazy_gettext('First Name'),
        'last_name': lazy_gettext('Last Name'),
        'username': lazy_gettext('User Name'),
        'password': lazy_gettext('Password'),
        'active': lazy_gettext('Is Active?'),
        'email': lazy_gettext('Email'),
        'roles': lazy_gettext('Role'),
        'last_login': lazy_gettext('Last login'),
        'login_count': lazy_gettext('Login count'),
        'fail_login_count': lazy_gettext('Failed login count'),
        'created_on': lazy_gettext('Created on'),
        'created_by': lazy_gettext('Created by'),
        'changed_on': lazy_gettext('Changed on'),
        'changed_by': lazy_gettext('Changed by')
    }

    description_columns = {
        'first_name': lazy_gettext(
            'Write the user first name or names'
        ),
        'last_name': lazy_gettext(
            'Write the user last name'
        ),
        'username': lazy_gettext(
            'Username valid for authentication on DB or LDAP, unused for OID auth'
        ),
        'password': lazy_gettext(
            'Please use a good password policy, this application does not check this for you'
        ),
        'active': lazy_gettext(
            'It\'s not a good policy to remove a user, just make it inactive'
        ),
        'email': lazy_gettext(
            'The user\'s email, this will also be used for OID auth'
        ),
        'roles': lazy_gettext(
            'The user role on the application, this will associate with a list of permissions'
        ),
        'conf_password': lazy_gettext(
            'Please rewrite the user\'s password to confirm'
        )
    }

    list_columns = [
        'first_name',
        'last_name',
        'username',
        'email',
        'active',
        'roles'
    ]
    show_columns = [
        'first_name',
        'last_name',
        'username',
        'active',
        'email',
        'roles'
    ]
    add_columns = [
        'first_name',
        'last_name',
        'username',
        'active',
        'email',
        'roles']
    edit_columns = [
        'first_name',
        'last_name',
        'username',
        'active',
        'email',
        'roles'
    ]
