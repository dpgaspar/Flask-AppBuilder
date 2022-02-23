import re

from flask import g, redirect, request, Response
from flask_appbuilder.api import BaseApi, safe
from flask_appbuilder.const import (
    API_SECURITY_ACCESS_TOKEN_KEY,
    API_SECURITY_EMAIL_KEY,
    API_SECURITY_FIRSTNAME_KEY,
    API_SECURITY_LASTNAME_KEY,
    API_SECURITY_METHOD_DB,
    API_SECURITY_METHOD_LDAP,
    API_SECURITY_METHOD_REMOTE,
    API_SECURITY_PASSWORD_KEY,
    API_SECURITY_PROVIDER_DB,
    API_SECURITY_PROVIDER_LDAP,
    API_SECURITY_REFRESH_TOKEN_KEY,
    API_SECURITY_USERNAME_KEY,
    API_SECURITY_VERSION,
)
from flask_appbuilder.security.decorators import has_access_api
from flask_appbuilder.security.schemas import login_post
from flask_appbuilder.views import expose
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
)
from flask_login import login_user, logout_user
import jwt
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash


class SecurityApi(BaseApi):
    resource_name = "security"
    version = API_SECURITY_VERSION
    openapi_spec_tag = "Security"

    def add_apispec_components(self, api_spec):
        super(SecurityApi, self).add_apispec_components(api_spec)
        jwt_scheme = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        api_spec.components.security_scheme("jwt", jwt_scheme)
        api_spec.components.security_scheme("jwt_refresh", jwt_scheme)

    @expose("/login", methods=["POST"])
    @safe
    def login(self) -> Response:
        """Login endpoint for the API returns a JWT and optionally a refresh token
        ---
        post:
          description: >-
            Authenticate and get a JWT access and refresh token
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    username:
                      description: The username for authentication
                      example: admin
                      type: string
                    password:
                      description: The password for authentication
                      example: complex-password
                      type: string
                    provider:
                      description: Choose an authentication provider
                      example: db
                      type: string
                      enum:
                      - db
                      - ldap
                    refresh:
                      description: If true a refresh token is provided also
                      example: true
                      type: boolean
          responses:
            200:
              description: Authentication Successful
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      access_token:
                        type: string
                      refresh_token:
                        type: string
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            500:
              $ref: '#/components/responses/500'
        """
        if not request.is_json:
            return self.response_400(message="Request payload is not JSON")
        try:
            login_payload = login_post.load(request.json)
        except ValidationError as error:
            return self.response_400(message=error.messages)

        # AUTH
        user = None
        if login_payload["provider"] == API_SECURITY_PROVIDER_DB:
            user = self.appbuilder.sm.auth_user_db(
                login_payload["username"], login_payload["password"]
            )
        elif login_payload["provider"] == API_SECURITY_PROVIDER_LDAP:
            user = self.appbuilder.sm.auth_user_ldap(
                login_payload["username"], login_payload["password"]
            )
        if not user:
            return self.response_401()

        # Identity can be any data that is json serializable
        resp = dict()
        resp[API_SECURITY_ACCESS_TOKEN_KEY] = create_access_token(
            identity=user.id, fresh=True
        )
        if "refresh" in login_payload and login_payload["refresh"]:
            resp[API_SECURITY_REFRESH_TOKEN_KEY] = create_refresh_token(
                identity=user.id
            )
        return self.response(200, **resp)

    @expose("/refresh", methods=["POST"])
    @jwt_refresh_token_required
    @safe
    def refresh(self) -> Response:
        """
            Security endpoint for the refresh token, so we can obtain a new
            token without forcing the user to login again
        ---
        post:
          description: >-
            Use the refresh token to get a new JWT access token
          responses:
            200:
              description: Refresh Successful
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      access_token:
                        description: A new refreshed access token
                        type: string
            401:
              $ref: '#/components/responses/401'
            500:
              $ref: '#/components/responses/500'
          security:
            - jwt_refresh: []
        """
        resp = {
            API_SECURITY_ACCESS_TOKEN_KEY: create_access_token(
                identity=get_jwt_identity(), fresh=False
            )
        }
        return self.response(200, **resp)


class AuthApi(BaseApi):
    """
    This provides the inbuilt authentication features through an API
    For more information see flask_appbuilder.security.modelviews

    flask_appbuilder.security.api.SecurityApi was used as reference but reworked,
    since it simply returns the jwt access and refresh token as json contrary to
    the functionality of    flask_appbuilder.security.modelviews where the tokens
    (with additional information) are stored in a signed httpOnly cookie

    Caveats: Doesn't support "Open ID" (since it is OpenID 2.0, which is deprecated).
             Doesn't support "REMOTE_USER"

    Fore more details see https://flask-appbuilder.readthedocs.io/en/latest/security.html
    """

    resource_name = "auth"

    @expose("/login", methods=["POST"])
    @safe
    def login(self, API_SECURITY_METHOD_KEY=None):
        """Login endpoint for the API, creates a session cookie
         ---
         post:
           description: >-
             Authenticate and create a session cookie
           requestBody:
             required: true
             content:
               application/json:
                 schema:
                   type: object
                   properties:
                     username:
                       description: The username for authentication
                       example: user1234
                       type: string
                       required: true
                     password:
                       description: The password for authentication
                       example: complex-password
                       type: string
                       required: true
                     method:
                       description: Choose an authentication method
                       example: db
                       type: string
                       enum:
                       - db
                       - ldap
                       required: true
           responses:
             200:
               description: Authentication Successful
             400:
               $ref: '#/components/responses/400'
             401:
               $ref: '#/components/responses/401'
             500:
               $ref: '#/components/responses/500'
         """

        if g.user is not None and g.user.is_authenticated:
            return self.response(200, message="User is already logged in")

        # Read and validate request body
        if not request.is_json:
            return self.response_400(message="Request payload is not JSON")
        username = request.json.get(API_SECURITY_USERNAME_KEY, None)
        password = request.json.get(API_SECURITY_PASSWORD_KEY, None)
        method = request.json.get(API_SECURITY_METHOD_KEY, None)

        if not username or not password or not method:
            return self.response_400(message="Missing required parameter")

        # Authenticate based on method
        user = None
        if method == API_SECURITY_METHOD_DB:
            user = self.appbuilder.sm.auth_user_db(username, password)
        elif method == API_SECURITY_METHOD_LDAP:
            user = self.appbuilder.sm.auth_user_ldap(username, password)

        elif method == API_SECURITY_METHOD_REMOTE:
            username = request.environ.get("REMOTE_USER")
            if username:
                user = self.appbuilder.sm.auth_user_remote_user(username)
        else:
            return self.response_400(message="Method {} not supported".format(method))
        if not user:
            return self.response_401()

        # Set session cookie
        login_user(user, remember=False)
        return self.response(200, message="Login successful")

    @expose("/login/<provider>", methods=["GET"])
    @safe
    def init_oauth(self, provider):
        """OAuth initiation endpoint for the API
         ---
          get:
            description: >-
              Initiate OAuth login
            parameters:
              - in: path
                name: provider
                schema:
                  type: str
                required: true
                description: Provider to authenticate against

            responses:
              302:
                $ref: '#/components/responses/202'
              500:
                $ref: '#/components/responses/500'
         """
        if g.user is not None and g.user.is_authenticated:
            return redirect(self.appbuilder.app.config["REDIRECT_URI"])

        if provider is None:
            return self.response_400(message="Missing required parameter")

        state = jwt.encode(
            request.args.to_dict(flat=False),
            self.appbuilder.app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        try:
            if provider == "twitter":
                # not works
                return self.appbuilder.sm.oauth_remotes[provider].authorize_redirect(
                    redirect_uri=request.base_url + "/callback"
                )
            else:
                return self.appbuilder.sm.oauth_remotes[provider].authorize_redirect(
                    redirect_uri=request.base_url + "/callback",
                    state=state.decode("ascii") if isinstance(state, bytes) else state,
                )

        except Exception:
            return self.response_500()

    @expose("/login/<provider>/callback")
    def oauth_callback(self, provider):
        """OAuth redirect endpoint for the API, creates a session cookie
           Make sure to add this endpoint as the redirect uri of your provider
         ---
          get:
            description: >-
              Authenticate and create a session cookie
            parameters:
              - in: path
                name: provider
                schema:
                  type: str
                required: true
                description: Provider to authenticate against

            responses:
              302:
                $ref: '#/components/responses/202'
              400:
                $ref: '#/components/responses/400'
              500:
                $ref: '#/components/responses/500'
         """
        if provider not in self.appbuilder.sm.oauth_remotes:
            return self.response_400(message="Provider not supported")
        resp = self.appbuilder.sm.oauth_remotes[provider].authorize_access_token()
        if resp is None:
            return self.response_400(message="Request for sign in was denied.")

        # Retrieves specific user info from the provider
        try:
            self.appbuilder.sm.set_oauth_session(provider, resp)
            userinfo = self.appbuilder.sm.oauth_user_info(provider, resp)
        except Exception:
            user = None
        else:
            # User email is not whitelisted
            if provider in self.appbuilder.sm.oauth_whitelists:
                whitelist = self.appbuilder.sm.oauth_whitelists[provider]
                allow = False
                for email in whitelist:
                    if "email" in userinfo and re.search(email, userinfo["email"]):
                        allow = True
                        break
                if not allow:
                    self.response_401()
            user = self.appbuilder.sm.auth_user_oauth(userinfo)
        if user is None:
            self.response_400(message="Invalid login. Please try again.")
        else:
            login_user(user)
            return redirect(self.appbuilder.app.config["REDIRECT_URI"])

    @has_access_api
    @expose("/logout", methods=["GET"])
    @safe
    def logout(self):
        """Logs the user out and deletes session cookie"""
        logout_user()
        return self.response(200, message="Logout successful")

    @expose("/signup", methods=["POST"])
    @safe
    def signup(self):
        """
        This endpoint creates a new user

        More info:
        - The base logic will register users for LDAP and OAuth automatically
          with a predefined model. DB will expect user data by the client
          using a predefined model.
        - To customize the registration flow for DB, LDAP or OAuth (for example
          to add custom data to registration) create a custom SecurityManager class.
          As a starting point see `auth_user_db`, `auth_user_ldap` or `auth_user_oauth`
          methods in flask_appbuilder.security.sqla/manager.manager.SecurityManager.
          Adjust the front end accordingly.
       ---
       post:
         description: >-
           Register user and create a session cookie
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   username:
                     description: The username of the new user
                     example: user1234
                     type: string
                     required: true
                   firstname:
                     description: The first name of the new user
                     example: John
                     type: string
                     required: true
                   lastname:
                     description: The last name of the new user
                     example: Doe
                     type: string
                     required: true
                   email:
                     description: The last name of the new user
                     example: Doe
                     type: string
                     required: true
                   password:
                     description: The password for authentication
                     example: complex-password
                     type: string
                     required: true
         responses:
           200:
             description: Authentication Successful
           400:
             $ref: '#/components/responses/400'
           500:
             $ref: '#/components/responses/500'
        """

        # read and validate data
        username = request.json.get(API_SECURITY_USERNAME_KEY, None)
        firstname = request.json.get(API_SECURITY_FIRSTNAME_KEY, None)
        lastname = request.json.get(API_SECURITY_LASTNAME_KEY, None)
        email = request.json.get(API_SECURITY_EMAIL_KEY, None)
        password = request.json.get(API_SECURITY_PASSWORD_KEY, None)

        if not username or not firstname or not lastname or not email or not password:
            return self.response_400(message="Missing required parameter")

        password = generate_password_hash(password)
        if not self.appbuilder.sm.add_user(
                username=username,
                email=email,
                first_name=firstname,
                last_name=lastname,
                role=self.appbuilder.sm.find_role(
                    self.appbuilder.sm.auth_user_registration_role
                ),
                hashed_password=password,
        ):
            return self.response_500()
        else:
            return self.response(200, message="Registration successful")

    @has_access_api
    @expose("/authenticate", methods=["GET"])
    @safe
    def authenticate(self):
        """
        Endpoint to authenticate the user
        ---
        get:
         description: >-
           Authenticate user
         responses:
           200:
             description: Authentication Successful
           500:
             $ref: '#/components/responses/500'
        """
        return self.response(200, message="Authentication successful")
