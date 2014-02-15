from ..fieldwidgets import BS3PasswordFieldWidget
from flask_wtf import validators
from flask import render_template, flash, redirect, session, url_for, request, g
from openid.consumer import discover
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL
from openid.extensions import ax
from openid.extensions.sreg import SRegRequest, SRegResponse
from flask.ext.openid import SessionWrapper, OpenIDResponse
from flask_wtf import EqualTo, PasswordField
from flask.ext.babelpkg import gettext, lazy_gettext
from flask_login import login_user, logout_user

from flask_appbuilder.models.datamodel import SQLAModel
from flask_appbuilder.views import BaseView, GeneralView, SimpleFormView, expose
from ..actions import action
from forms import LoginForm_db, LoginForm_oid, ResetPasswordForm
from models import User, Permission, PermissionView, Role, ViewMenu
from decorators import has_access


class PermissionGeneralView(GeneralView):
    route_base = '/permissions'

    datamodel = SQLAModel(Permission)

    list_title = lazy_gettext('List Base Permissions')
    show_title = lazy_gettext('Show Base Permission')
    add_title = lazy_gettext('Add Base Permission')
    edit_title = lazy_gettext('Edit Base Permission')

    label_columns = {'name': lazy_gettext('Name')}


class ViewMenuGeneralView(GeneralView):
    route_base = '/viewmenus'

    datamodel = SQLAModel(ViewMenu)

    list_title = lazy_gettext('List View Menus')
    show_title = lazy_gettext('Show View Menu')
    add_title = lazy_gettext('Add View Menu')
    edit_title = lazy_gettext('Edit View Menu')

    label_columns = {'name': lazy_gettext('Name')}


class PermissionViewGeneralView(GeneralView):
    route_base = '/permissionviews'

    datamodel = SQLAModel(PermissionView)

    list_title = lazy_gettext('List Permissions on Views/Menus')
    show_title = lazy_gettext('Show Permission on Views/Menus')
    add_title = lazy_gettext('Add Permission on Views/Menus')
    edit_title = lazy_gettext('Edit Permission on Views/Menus')

    label_columns = {'permission': lazy_gettext('Permission'), 'view_menu': lazy_gettext('View/Menu')}
    list_columns = ['permission', 'view_menu']
    show_columns = ['permission', 'view_menu']
    search_columns = ['permission', 'view_menu']


class ResetMyPasswordView(SimpleFormView):
    """
    View for reseting own user password
    """
    route_base = '/resetmypassword'

    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    redirect_url = '/'

    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        self.baseapp.sm.reset_password(g.user.id, form.password.data)
        flash(unicode(self.message), 'info')


class ResetPasswordView(SimpleFormView):
    """
    View for reseting all users password
    """

    route_base = '/resetpassword'

    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    redirect_url = '/'

    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        pk = request.args.get('pk')
        self.baseapp.sm.reset_password(pk, form.password.data)
        flash(unicode(self.message), 'info')


class UserGeneralView(GeneralView):
    route_base = '/users'
    datamodel = SQLAModel(User)

    list_title = lazy_gettext('List Users')
    show_title = lazy_gettext('Show User')
    add_title = lazy_gettext('Add User')
    edit_title = lazy_gettext('Edit User')

    label_columns = {'get_full_name': lazy_gettext('Full Name'),
                     'first_name': lazy_gettext('First Name'),
                     'last_name': lazy_gettext('Last Name'),
                     'username': lazy_gettext('User Name'),
                     'password': lazy_gettext('Password'),
                     'active': lazy_gettext('Is Active?'),
                     'email': lazy_gettext('EMail'),
                     'role': lazy_gettext('Role')}
    description_columns = {'first_name': lazy_gettext('Write the user first name or names'),
                           'last_name': lazy_gettext('Write the user last name'),
                           'username': lazy_gettext(
                               'Username valid for authentication on DB or LDAP, unused for OID auth'),
                           'password': lazy_gettext(
                               'Please use a good password policy, this application does not check this for you'),
                           'active': lazy_gettext('Its not a good policy to remove a user, just make it inactive'),
                           'email': lazy_gettext('The users email, this will also be used for OID auth'),
                           'role': lazy_gettext(
                               'The user role on the application, this will associate with a list of permissions'),
                           'conf_password': lazy_gettext('Please rewrite the users password to confirm')}
    list_columns = ['full_name', 'username', 'email', 'active', 'role']
    show_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role']
    order_columns = ['username', 'email']
    search_columns = ['first_name', 'last_name', 'username', 'email', 'role']

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role']
    edit_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role']

    user_info_title = lazy_gettext("Your user information")

    show_additional_links = []


class UserOIDGeneralView(UserGeneralView):
    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        widgets = self._get_show_widget(g.user.id)

        return render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               baseapp=self.baseapp
        )


class UserDBGeneralView(UserGeneralView):
    add_form_extra_fields = {'password': PasswordField(gettext('Password'),
                                                       description=gettext(
                                                           'Please use a good password policy, this application does not check this for you'),
                                                       validators=[validators.Required()],
                                                       widget=BS3PasswordFieldWidget()),
                             'conf_password': PasswordField(gettext('Confirm Password'),
                                                            description=gettext(
                                                                'Please rewrite the users password to confirm'),
                                                            validators=[EqualTo('password', message=gettext(
                                                                'Passwords must match'))],
                                                            widget=BS3PasswordFieldWidget())}

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role', 'password', 'conf_password']

    @expose('/show/<int:pk>', methods=['GET'])
    @has_access
    def show(self, pk):
        actions = {}
        actions['resetpasswords'] = self.actions.get('resetpasswords')
        widgets = self._get_show_widget(pk, actions=actions)
        return render_template(self.show_template,
                               pk=pk,
                               title=self.show_title,
                               widgets=widgets,
                               baseapp=self.baseapp,
                               related_views=self._related_views)


    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        actions = {}
        actions['resetmypassword'] = self.actions.get('resetmypassword')
        widgets = self._get_show_widget(g.user.id, actions=actions)
        return render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               baseapp=self.baseapp,
        )

    @action('resetmypassword', lazy_gettext("Reset my password"), "", "fa-lock")
    def resetmypassword(self, item):
        return redirect(url_for('ResetMyPasswordView.this_form_get'))

    @action('resetpasswords', lazy_gettext("Reset Password"), "", "fa-lock")
    def resetpasswords(self, item):
        return redirect(url_for('ResetPasswordView.this_form_get', pk=item.id))


class RoleGeneralView(GeneralView):
    route_base = '/roles'

    datamodel = SQLAModel(Role)

    list_title = lazy_gettext('List Roles')
    show_title = lazy_gettext('Show Role')
    add_title = lazy_gettext('Add Role')
    edit_title = lazy_gettext('Edit Role')

    label_columns = {'name': lazy_gettext('Name'), 'permissions': lazy_gettext('Permissions')}
    list_columns = ['name', 'permissions']
    show_columns = ['name', 'permissions']
    order_columns = ['name']
    search_columns = ['name']


class AuthView(BaseView):
    route_base = ''
    login_db_template = 'appbuilder/general/security/login_db.html'
    login_oid_template = 'appbuilder/general/security/login_oid.html'

    invalid_login_message = lazy_gettext('Invalid login. Please try again.')

    title = lazy_gettext('Sign In')

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        pass

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect('/')


class AuthDBView(AuthView):
    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.baseapp.sm.auth_user_db(form.username.data, form.password.data)
            if not user:
                flash(unicode(self.invalid_login_message), 'warning')
                return redirect('/login')
            login_user(user, remember=False)
            return redirect('/')
        return render_template(self.login_db_template,
                               title=self.title,
                               form=form,
                               baseapp=self.baseapp
        )


class AuthOIDView(AuthView):
    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):
        if flag:
            self.oid_login_handler(self.login, self.baseapp.sm.oid)
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return self.baseapp.sm.oid.try_login(form.openid.data, ask_for=['email'])
        return render_template(self.login_oid_template,
                               title=self.title,
                               form=form,
                               providers=self.baseapp.app.config['OPENID_PROVIDERS'],
                               baseapp=self.baseapp
        )

    def oid_login_handler(self, f, oid):
        if request.args.get('openid_complete') != u'yes':
            return f(False)
        consumer = Consumer(SessionWrapper(self), oid.store_factory())
        openid_response = consumer.complete(request.args.to_dict(),
                                            oid.get_current_url())
        if openid_response.status == SUCCESS:
            return oid.after_login_func(OpenIDResponse(openid_response, []))
        elif openid_response.status == CANCEL:
            oid.signal_error(u'The request was cancelled')
            return redirect(oid.get_current_url())
        oid.signal_error(u'OpenID authentication error')
        return redirect(oid.get_current_url())

    def after_login(self, resp):
        if resp.email is None or resp.email == "":
            flash(unicode(self.invalid_login_message), 'warning')
            return redirect('appbuilder/general/security/login_oid.html')
        user = self.baseapp.sm.auth_user_oid(resp.email)
        if user is None:
            flash(unicode(self.invalid_login_message), 'warning')
            return redirect('appbuilder/general/security/login_oid.html')
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(user, remember=remember_me)
        return redirect('/')




