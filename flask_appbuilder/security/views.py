import datetime
import logging
import re
from typing import Any, List, Optional

from flask import abort, current_app, flash, g, redirect, request, session, url_for
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.actions import action
from flask_appbuilder.baseviews import BaseView
from flask_appbuilder.charts.views import DirectByChartView
from flask_appbuilder.fieldwidgets import BS3PasswordFieldWidget
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder.security.forms import (
    DynamicForm,
    LoginForm_db,
    LoginForm_oid,
    ResetPasswordForm,
    SelectDataRequired,
    UserInfoEdit,
)
from flask_appbuilder.security.utils import generate_random_string
from flask_appbuilder.utils.base import get_safe_redirect, lazy_formatter_gettext
from flask_appbuilder.validators import PasswordComplexityValidator
from flask_appbuilder.views import expose, ModelView, SimpleFormView
from flask_appbuilder.widgets import ListWidget, ShowWidget
from flask_babel import lazy_gettext
from flask_login import login_user, logout_user
import jwt
from werkzeug.security import generate_password_hash
from werkzeug.wrappers import Response as WerkzeugResponse
from wtforms import PasswordField, validators
from wtforms.validators import EqualTo


log = logging.getLogger(__name__)


class PermissionModelView(ModelView):
    route_base = "/permissions"
    base_permissions = ["can_list"]

    list_title = lazy_gettext("List Base Permissions")
    show_title = lazy_gettext("Show Base Permission")
    add_title = lazy_gettext("Add Base Permission")
    edit_title = lazy_gettext("Edit Base Permission")

    label_columns = {"name": lazy_gettext("Name")}


class ViewMenuModelView(ModelView):
    route_base = "/viewmenus"
    base_permissions = ["can_list"]

    list_title = lazy_gettext("List View Menus")
    show_title = lazy_gettext("Show View Menu")
    add_title = lazy_gettext("Add View Menu")
    edit_title = lazy_gettext("Edit View Menu")

    label_columns = {"name": lazy_gettext("Name")}


class PermissionViewModelView(ModelView):
    route_base = "/permissionviews"
    base_permissions = ["can_list"]

    list_title = lazy_gettext("List Permissions on Views/Menus")
    show_title = lazy_gettext("Show Permission on Views/Menus")
    add_title = lazy_gettext("Add Permission on Views/Menus")
    edit_title = lazy_gettext("Edit Permission on Views/Menus")

    label_columns = {
        "permission": lazy_gettext("Permission"),
        "view_menu": lazy_gettext("View/Menu"),
    }
    list_columns = ["permission", "view_menu"]


class ResetMyPasswordView(SimpleFormView):
    """
    View for resetting own user password
    """

    route_base = "/resetmypassword"
    form = ResetPasswordForm
    form_title = lazy_gettext("Reset Password Form")
    redirect_url = "/"
    message = lazy_gettext("Password Changed")

    def form_post(self, form: DynamicForm) -> None:
        self.appbuilder.sm.reset_password(g.user.id, form.password.data)
        flash(as_unicode(self.message), "info")


class ResetPasswordView(SimpleFormView):
    """
    View for reseting all users password
    """

    route_base = "/resetpassword"
    form = ResetPasswordForm
    form_title = lazy_gettext("Reset Password Form")
    redirect_url = "/"
    message = lazy_gettext("Password Changed")

    def form_post(self, form: DynamicForm) -> None:
        pk = request.args.get("pk")
        self.appbuilder.sm.reset_password(pk, form.password.data)
        flash(as_unicode(self.message), "info")


class UserInfoEditView(SimpleFormView):
    form = UserInfoEdit
    form_title = lazy_gettext("Edit User Information")
    redirect_url = "/"
    message = lazy_gettext("User information changed")

    def form_get(self, form: DynamicForm) -> None:
        item = self.appbuilder.sm.get_user_by_id(g.user.id)
        # fills the form generic solution
        for key, value in form.data.items():
            if key == "csrf_token":
                continue
            form_field = getattr(form, key)
            form_field.data = getattr(item, key)

    def form_post(self, form: DynamicForm) -> None:
        form = self.form.refresh(request.form)
        item = self.appbuilder.sm.get_user_by_id(g.user.id)
        form.populate_obj(item)
        self.appbuilder.sm.update_user(item)
        flash(as_unicode(self.message), "info")


def _roles_custom_formatter(string: str) -> str:
    if current_app.config.get("AUTH_ROLES_SYNC_AT_LOGIN", False):
        string += (
            ". <div class='alert alert-warning' role='alert'>"
            "AUTH_ROLES_SYNC_AT_LOGIN is enabled, changes to this field will "
            "not persist between user logins."
            "</div>"
        )
    return string


class UserModelView(ModelView):
    route_base = "/users"

    list_title = lazy_gettext("List Users")
    show_title = lazy_gettext("Show User")
    add_title = lazy_gettext("Add User")
    edit_title = lazy_gettext("Edit User")

    label_columns = {
        "get_full_name": lazy_gettext("Full Name"),
        "first_name": lazy_gettext("First Name"),
        "last_name": lazy_gettext("Last Name"),
        "username": lazy_gettext("User Name"),
        "password": lazy_gettext("Password"),
        "active": lazy_gettext("Is Active?"),
        "email": lazy_gettext("Email"),
        "roles": lazy_gettext("Role"),
        "last_login": lazy_gettext("Last login"),
        "login_count": lazy_gettext("Login count"),
        "fail_login_count": lazy_gettext("Failed login count"),
        "created_on": lazy_gettext("Created on"),
        "created_by": lazy_gettext("Created by"),
        "changed_on": lazy_gettext("Changed on"),
        "changed_by": lazy_gettext("Changed by"),
    }

    description_columns = {
        "first_name": lazy_gettext("Write the user first name or names"),
        "last_name": lazy_gettext("Write the user last name"),
        "username": lazy_gettext(
            "Username valid for authentication on DB or LDAP, unused for OID auth"
        ),
        "password": lazy_gettext("The user's password for authentication"),
        "active": lazy_gettext(
            "It's not a good policy to remove a user, just make it inactive"
        ),
        "email": lazy_gettext("The user's email, this will also be used for OID auth"),
        "roles": lazy_formatter_gettext(
            "The user role on the application,"
            " this will associate with a list of permissions",
            _roles_custom_formatter,
        ),
        "conf_password": lazy_gettext("Please rewrite the user's password to confirm"),
    }

    list_columns = ["first_name", "last_name", "username", "email", "active", "roles"]

    show_fieldsets = [
        (
            lazy_gettext("User info"),
            {"fields": ["username", "active", "roles", "login_count"]},
        ),
        (
            lazy_gettext("Personal Info"),
            {"fields": ["first_name", "last_name", "email"], "expanded": True},
        ),
        (
            lazy_gettext("Audit Info"),
            {
                "fields": [
                    "last_login",
                    "fail_login_count",
                    "created_on",
                    "created_by",
                    "changed_on",
                    "changed_by",
                ],
                "expanded": False,
            },
        ),
    ]

    user_show_fieldsets = [
        (
            lazy_gettext("User info"),
            {"fields": ["username", "active", "roles", "login_count"]},
        ),
        (
            lazy_gettext("Personal Info"),
            {"fields": ["first_name", "last_name", "email"], "expanded": True},
        ),
    ]
    search_columns = [
        "first_name",
        "last_name",
        "username",
        "email",
        "active",
        "roles",
        "created_on",
        "changed_on",
        "last_login",
        "login_count",
        "fail_login_count",
    ]

    add_columns = ["first_name", "last_name", "username", "active", "email", "roles"]
    edit_columns = ["first_name", "last_name", "username", "active", "email", "roles"]
    user_info_title = lazy_gettext("Your user information")

    @expose("/userinfo/")
    @has_access
    def userinfo(self) -> WerkzeugResponse:
        item = self.datamodel.get(g.user.id, self._base_filters)
        widgets = self._get_show_widget(
            g.user.id, item, show_fieldsets=self.user_show_fieldsets
        )
        self.update_redirect()
        return self.render_template(
            self.show_template,
            title=self.user_info_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
        )

    @action("userinfoedit", lazy_gettext("Edit User"), "", "fa-edit", multiple=False)
    def userinfoedit(self, item: Any) -> WerkzeugResponse:
        return redirect(
            url_for(self.appbuilder.sm.userinfoeditview.__name__ + ".this_form_get")
        )


class UserOIDModelView(UserModelView):
    """
    View that add OID specifics to User view.
    Override to implement your own custom view.
    Then override useroidmodelview property on SecurityManager
    """

    pass


class UserLDAPModelView(UserModelView):
    """
    View that add LDAP specifics to User view.
    Override to implement your own custom view.
    Then override userldapmodelview property on SecurityManager
    """

    pass


class UserOAuthModelView(UserModelView):
    """
    View that add OAUTH specifics to User view.
    Override to implement your own custom view.
    Then override userldapmodelview property on SecurityManager
    """

    pass


class UserRemoteUserModelView(UserModelView):
    """
    View that add REMOTE_USER specifics to User view.
    Override to implement your own custom view.
    Then override userldapmodelview property on SecurityManager
    """

    pass


class UserDBModelView(UserModelView):
    """
    View that add DB specifics to User view.
    Override to implement your own custom view.
    Then override userdbmodelview property on SecurityManager
    """

    add_form_extra_fields = {
        "password": PasswordField(
            lazy_gettext("Password"),
            description=lazy_gettext("The user's password for authentication"),
            validators=[validators.DataRequired(), PasswordComplexityValidator()],
            widget=BS3PasswordFieldWidget(),
        ),
        "conf_password": PasswordField(
            lazy_gettext("Confirm Password"),
            description=lazy_gettext("Please rewrite the user's password to confirm"),
            validators=[
                validators.DataRequired(),
                EqualTo("password", message=lazy_gettext("Passwords must match")),
            ],
            widget=BS3PasswordFieldWidget(),
        ),
    }

    add_columns = [
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
        "roles",
        "password",
        "conf_password",
    ]

    validators_columns = {"roles": [SelectDataRequired()]}

    @expose("/show/<pk>", methods=["GET"])
    @has_access
    def show(self, pk: Any) -> WerkzeugResponse:
        actions = dict()
        actions["resetpasswords"] = self.actions.get("resetpasswords")
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            abort(404)
        widgets = self._get_show_widget(pk, item, actions=actions)
        self.update_redirect()
        return self.render_template(
            self.show_template,
            pk=pk,
            title=self.show_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
            related_views=self._related_views,
        )

    @expose("/userinfo/")
    @has_access
    def userinfo(self) -> WerkzeugResponse:
        actions = dict()
        actions["resetmypassword"] = self.actions.get("resetmypassword")
        actions["userinfoedit"] = self.actions.get("userinfoedit")

        item = self.datamodel.get(g.user.id, self._base_filters)
        widgets = self._get_show_widget(
            g.user.id, item, actions=actions, show_fieldsets=self.user_show_fieldsets
        )
        self.update_redirect()
        return self.render_template(
            self.show_template,
            title=self.user_info_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
        )

    @action(
        "resetmypassword",
        lazy_gettext("Reset my password"),
        "",
        "fa-lock",
        multiple=False,
    )
    def resetmypassword(self, item: Any):
        return redirect(
            url_for(self.appbuilder.sm.resetmypasswordview.__name__ + ".this_form_get")
        )

    @action(
        "resetpasswords", lazy_gettext("Reset Password"), "", "fa-lock", multiple=False
    )
    def resetpasswords(self, item: Any) -> WerkzeugResponse:
        return redirect(
            url_for(
                self.appbuilder.sm.resetpasswordview.__name__ + ".this_form_get",
                pk=item.id,
            )
        )

    def pre_update(self, item: Any) -> None:
        item.changed_on = datetime.datetime.now()
        item.changed_by_fk = g.user.id

    def pre_add(self, item: Any) -> None:
        item.password = generate_password_hash(item.password)


class UserStatsChartView(DirectByChartView):
    chart_title = lazy_gettext("User Statistics")
    label_columns = {
        "username": lazy_gettext("User Name"),
        "login_count": lazy_gettext("Login count"),
        "fail_login_count": lazy_gettext("Failed login count"),
    }

    search_columns = UserModelView.search_columns

    definitions = [
        {"label": "Login Count", "group": "username", "series": ["login_count"]},
        {
            "label": "Failed Login Count",
            "group": "username",
            "series": ["fail_login_count"],
        },
    ]


class RoleListWidget(ListWidget):
    template = "appbuilder/general/widgets/roles/list.html"

    def __init__(self, **kwargs):
        kwargs["appbuilder"] = current_app.appbuilder
        super().__init__(**kwargs)


class RoleShowWidget(ShowWidget):
    template = "appbuilder/general/widgets/roles/show.html"

    def __init__(self, **kwargs):
        kwargs["appbuilder"] = current_app.appbuilder
        super().__init__(**kwargs)


class RoleModelView(ModelView):
    route_base = "/roles"

    list_title = lazy_gettext("List Roles")
    show_title = lazy_gettext("Show Role")
    add_title = lazy_gettext("Add Role")
    edit_title = lazy_gettext("Edit Role")

    list_widget = RoleListWidget
    show_widget = RoleShowWidget

    label_columns = {
        "name": lazy_gettext("Name"),
        "permissions": lazy_gettext("Permissions"),
    }
    list_columns = ["name", "permissions"]
    show_columns = ["name", "permissions"]
    edit_columns = ["name", "permissions"]
    add_columns = edit_columns
    order_columns = ["name"]

    @action(
        "copyrole",
        lazy_gettext("Copy Role"),
        lazy_gettext("Copy the selected roles?"),
        icon="fa-copy",
        single=False,
    )
    def copy_role(self, items):
        self.update_redirect()
        for item in items:
            new_role = item.__class__()
            new_role.name = item.name
            new_role.permissions = item.permissions
            new_role.name = new_role.name + " copy"
            self.datamodel.add(new_role)
        return redirect(self.get_redirect())


class RegisterUserModelView(ModelView):
    route_base = "/registeruser"
    base_permissions = ["can_list", "can_show", "can_delete"]
    list_title = lazy_gettext("List of Registration Requests")
    show_title = lazy_gettext("Show Registration")
    list_columns = ["username", "registration_date", "email"]
    show_exclude_columns = ["password"]
    search_exclude_columns = ["password"]


class AuthView(BaseView):
    route_base = ""
    login_template = ""
    invalid_login_message = lazy_gettext("Invalid login. Please try again.")
    title = lazy_gettext("Sign In")

    @expose("/login/", methods=["GET", "POST"])
    def login(self):
        pass

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(
            self.appbuilder.app.config.get(
                "LOGOUT_REDIRECT_URL", self.appbuilder.get_url_for_index
            )
        )


class AuthDBView(AuthView):
    login_template = "appbuilder/general/security/login_db.html"

    @expose("/login/", methods=["GET", "POST"])
    def login(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_db()
        if form.validate_on_submit():
            next_url = get_safe_redirect(request.args.get("next", ""))
            user = self.appbuilder.sm.auth_user_db(
                form.username.data, form.password.data
            )
            if not user:
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login_with(next_url))
            login_user(user, remember=False)
            return redirect(next_url)
        return self.render_template(
            self.login_template, title=self.title, form=form, appbuilder=self.appbuilder
        )


class AuthLDAPView(AuthView):
    login_template = "appbuilder/general/security/login_ldap.html"

    @expose("/login/", methods=["GET", "POST"])
    def login(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_db()
        if form.validate_on_submit():
            next_url = get_safe_redirect(request.args.get("next", ""))
            user = self.appbuilder.sm.auth_user_ldap(
                form.username.data, form.password.data
            )
            if not user:
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login_with(next_url))
            login_user(user, remember=False)
            return redirect(next_url)
        return self.render_template(
            self.login_template, title=self.title, form=form, appbuilder=self.appbuilder
        )


class AuthOIDView(AuthView):
    login_template = "appbuilder/general/security/login_oid.html"
    oid_ask_for = ["email"]
    oid_ask_for_optional: List[str] = []

    @expose("/login/", methods=["GET", "POST"])
    def login(self, flag=True) -> WerkzeugResponse:
        @self.appbuilder.sm.oid.loginhandler
        def login_handler(self):
            if g.user is not None and g.user.is_authenticated:
                return redirect(self.appbuilder.get_url_for_index)
            form = LoginForm_oid()
            if form.validate_on_submit():
                session["remember_me"] = form.remember_me.data
                identity_url = self.appbuilder.sm.get_oid_identity_url(form.openid.data)
                if identity_url is None:
                    flash(as_unicode(self.invalid_login_message), "warning")
                    return redirect(self.appbuilder.get_url_for_login)
                return self.appbuilder.sm.oid.try_login(
                    identity_url,
                    ask_for=self.oid_ask_for,
                    ask_for_optional=self.oid_ask_for_optional,
                )
            return self.render_template(
                self.login_template,
                title=self.title,
                form=form,
                providers=self.appbuilder.sm.openid_providers,
                appbuilder=self.appbuilder,
            )

        @self.appbuilder.sm.oid.after_login
        def after_login(resp):
            if resp.email is None or resp.email == "":
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login)
            user = self.appbuilder.sm.auth_user_oid(resp.email)
            if user is None:
                flash(as_unicode(self.invalid_login_message), "warning")
                return redirect(self.appbuilder.get_url_for_login)
            remember_me = False
            if "remember_me" in session:
                remember_me = session["remember_me"]
                session.pop("remember_me", None)

            log.warning(
                "AUTH_OID is deprecated and will be removed in version 5. "
                "Migrate to other authentication methods."
            )
            login_user(user, remember=remember_me)
            next_url = request.args.get("next", "")
            return redirect(get_safe_redirect(next_url))

        return login_handler(self)


class AuthOAuthView(AuthView):
    login_template = "appbuilder/general/security/login_oauth.html"

    @expose("/login/")
    @expose("/login/<provider>")
    def login(self, provider: Optional[str] = None) -> WerkzeugResponse:
        log.debug("Provider: %s", provider)
        if g.user is not None and g.user.is_authenticated:
            log.debug("Already authenticated %s", g.user)
            return redirect(self.appbuilder.get_url_for_index)

        if provider is None:
            return self.render_template(
                self.login_template,
                providers=self.appbuilder.sm.oauth_providers,
                title=self.title,
                appbuilder=self.appbuilder,
            )

        log.debug("Going to call authorize for: %s", provider)
        random_state = generate_random_string()
        state = jwt.encode(
            request.args.to_dict(flat=False), random_state, algorithm="HS256"
        )
        session["oauth_state"] = random_state
        try:
            if provider == "twitter":
                return self.appbuilder.sm.oauth_remotes[provider].authorize_redirect(
                    redirect_uri=url_for(
                        ".oauth_authorized",
                        provider=provider,
                        _external=True,
                        state=state,
                    )
                )
            else:
                return self.appbuilder.sm.oauth_remotes[provider].authorize_redirect(
                    redirect_uri=url_for(
                        ".oauth_authorized", provider=provider, _external=True
                    ),
                    state=state.decode("ascii") if isinstance(state, bytes) else state,
                )
        except Exception as e:
            log.error("Error on OAuth authorize: %s", e)
            flash(as_unicode(self.invalid_login_message), "warning")
            return redirect(self.appbuilder.get_url_for_index)

    @expose("/oauth-authorized/<provider>")
    def oauth_authorized(self, provider: str) -> WerkzeugResponse:
        log.debug("Authorized init")
        if provider not in self.appbuilder.sm.oauth_remotes:
            flash("Provider not supported.", "warning")
            log.warning("OAuth authorized got an unknown provider %s", provider)
            return redirect(self.appbuilder.get_url_for_login)
        try:
            resp = self.appbuilder.sm.oauth_remotes[provider].authorize_access_token()
        except Exception as e:
            log.error("Error authorizing OAuth access token: %s", e)
            flash("The request to sign in was denied.", "error")
            return redirect(self.appbuilder.get_url_for_login)
        if resp is None:
            flash("You denied the request to sign in.", "warning")
            return redirect(self.appbuilder.get_url_for_login)
        log.debug("OAUTH Authorized resp: %s", resp)
        # Retrieves specific user info from the provider
        try:
            self.appbuilder.sm.set_oauth_session(provider, resp)
            userinfo = self.appbuilder.sm.oauth_user_info(provider, resp)
        except Exception as e:
            log.error("Error returning OAuth user info: %s", e)
            user = None
        else:
            log.debug("User info retrieved from %s: %s", provider, userinfo)
            # User email is not whitelisted
            if provider in self.appbuilder.sm.oauth_whitelists:
                whitelist = self.appbuilder.sm.oauth_whitelists[provider]
                allow = False
                for email in whitelist:
                    if "email" in userinfo and re.search(email, userinfo["email"]):
                        allow = True
                        break
                if not allow:
                    flash("You are not authorized.", "warning")
                    return redirect(self.appbuilder.get_url_for_login)
            else:
                log.debug("No whitelist for OAuth provider")
            user = self.appbuilder.sm.auth_user_oauth(userinfo)

        if user is None:
            flash(as_unicode(self.invalid_login_message), "warning")
            return redirect(self.appbuilder.get_url_for_login)
        else:
            try:
                state = jwt.decode(
                    request.args["state"], session["oauth_state"], algorithms=["HS256"]
                )
            except (jwt.InvalidTokenError, KeyError):
                flash(as_unicode("Invalid state signature"), "warning")
                return redirect(self.appbuilder.get_url_for_login)

            login_user(user)
            next_url = self.appbuilder.get_url_for_index
            # Check if there is a next url on state
            if "next" in state and len(state["next"]) > 0:
                next_url = get_safe_redirect(state["next"][0])
            return redirect(next_url)


class AuthRemoteUserView(AuthView):
    login_template = ""

    @expose("/login/")
    def login(self) -> WerkzeugResponse:
        username = request.environ.get(self.appbuilder.sm.auth_remote_user_env_var)
        if g.user is not None and g.user.is_authenticated:
            next_url = request.args.get("next", "")
            return redirect(get_safe_redirect(next_url))
        if username:
            user = self.appbuilder.sm.auth_user_remote_user(username)
            if user is None:
                flash(as_unicode(self.invalid_login_message), "warning")
            else:
                login_user(user)
        else:
            flash(as_unicode(self.invalid_login_message), "warning")
        next_url = request.args.get("next", "")
        return redirect(get_safe_redirect(next_url))
