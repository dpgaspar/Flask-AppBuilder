import datetime
import logging
import uuid
import sys
from flask import render_template, flash, redirect, session, url_for, request, g
from werkzeug.security import generate_password_hash
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL
from flask.ext.openid import SessionWrapper, OpenIDResponse, OpenID
from wtforms import validators, PasswordField
from wtforms.validators import EqualTo
from flask.ext.babelpkg import gettext, lazy_gettext
from flask_login import login_user, logout_user

from flask_appbuilder.models.datamodel import SQLAModel
from flask_appbuilder.views import BaseView, ModelView, SimpleFormView, expose, PublicFormView
from flask_appbuilder.charts.views import DirectByChartView

from ..fieldwidgets import BS3PasswordFieldWidget
from ..actions import action
from ..validators import Unique
from .._compat import as_unicode
from .forms import LoginForm_db, LoginForm_oid, ResetPasswordForm, RegisterUserDBForm, RegisterUserOIDForm
from .models import User, Permission, PermissionView, Role, ViewMenu, RegisterUser
from .decorators import has_access

log = logging.getLogger(__name__)


class PermissionModelView(ModelView):
    route_base = '/permissions'
    base_permissions = ['can_list']
    datamodel = SQLAModel(Permission)

    list_title = lazy_gettext('List Base Permissions')
    show_title = lazy_gettext('Show Base Permission')
    add_title = lazy_gettext('Add Base Permission')
    edit_title = lazy_gettext('Edit Base Permission')

    label_columns = {'name': lazy_gettext('Name')}


class ViewMenuModelView(ModelView):
    route_base = '/viewmenus'
    base_permissions = ['can_list']
    datamodel = SQLAModel(ViewMenu)

    list_title = lazy_gettext('List View Menus')
    show_title = lazy_gettext('Show View Menu')
    add_title = lazy_gettext('Add View Menu')
    edit_title = lazy_gettext('Edit View Menu')

    label_columns = {'name': lazy_gettext('Name')}


class PermissionViewModelView(ModelView):
    route_base = '/permissionviews'
    base_permissions = ['can_list']
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
        View for resetting own user password
    """
    route_base = '/resetmypassword'
    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    redirect_url = '/'
    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        self.appbuilder.sm.reset_password(g.user.id, form.password.data)
        flash(as_unicode(self.message), 'info')


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
        self.appbuilder.sm.reset_password(pk, form.password.data)
        flash(as_unicode(self.message), 'info')


class UserModelView(ModelView):
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
                     'role': lazy_gettext('Role'),
                     'last_login': lazy_gettext('Last login'),
                     'login_count': lazy_gettext('Login count'),
                     'fail_login_count': lazy_gettext('Failed login count'),
                     'created_on': lazy_gettext('Created on'),
                     'created_by': lazy_gettext('Created by'),
                     'changed_on': lazy_gettext('Changed on'),
                     'changed_by': lazy_gettext('Changed by')}

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

    list_columns = ['first_name', 'last_name', 'username', 'email', 'active', 'role']

    show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'role', 'login_count']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
        (lazy_gettext('Audit Info'),
         {'fields': ['last_login', 'fail_login_count', 'created_on',
                     'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
    ]

    user_show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'role', 'login_count']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
    ]

    order_columns = ['first_name', 'last_name', 'username', 'email']
    search_columns = ['first_name', 'last_name', 'username', 'email', 'role', 'active',
                      'created_by', 'changed_by', 'changed_on', 'changed_by', 'login_count']

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role']
    edit_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role']
    user_info_title = lazy_gettext("Your user information")


class UserOIDModelView(UserModelView):
    """
        View that add OID specifics to User view.
        Override to implement your own custom view.
        Then override useroidmodelview property on SecurityManager
    """

    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        widgets = self._get_show_widget(g.user.id, show_fieldsets=self.user_show_fieldsets)
        self.update_redirect()
        return render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder)


class UserLDAPModelView(UserModelView):
    """
        View that add LDAP specifics to User view.
        Override to implement your own custom view.
        Then override userldapmodelview property on SecurityManager
    """

    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        widgets = self._get_show_widget(g.user.id, show_fieldsets=self.user_show_fieldsets)
        self.update_redirect()
        return render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder)


class UserDBModelView(UserModelView):
    """
        View that add DB specifics to User view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """
    add_form_extra_fields = {'password': PasswordField(lazy_gettext('Password'),
                                                       description=lazy_gettext(
                                                           'Please use a good password policy, this application does not check this for you'),
                                                       validators=[validators.DataRequired()],
                                                       widget=BS3PasswordFieldWidget()),
                             'conf_password': PasswordField(lazy_gettext('Confirm Password'),
                                                            description=lazy_gettext(
                                                                'Please rewrite the users password to confirm'),
                                                            validators=[EqualTo('password', message=lazy_gettext(
                                                                'Passwords must match'))],
                                                            widget=BS3PasswordFieldWidget())}

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'role', 'password', 'conf_password']


    @expose('/show/<int:pk>', methods=['GET'])
    @has_access
    def show(self, pk):
        actions = {}
        actions['resetpasswords'] = self.actions.get('resetpasswords')
        widgets = self._get_show_widget(pk, actions=actions)
        self.update_redirect()
        return render_template(self.show_template,
                               pk=pk,
                               title=self.show_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder,
                               related_views=self._related_views)


    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        actions = {}
        actions['resetmypassword'] = self.actions.get('resetmypassword')
        widgets = self._get_show_widget(g.user.id, actions=actions, show_fieldsets=self.user_show_fieldsets)
        self.update_redirect()
        return render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder,
        )

    @action('resetmypassword', lazy_gettext("Reset my password"), "", "fa-lock", multiple=False)
    def resetmypassword(self, item):
        return redirect(url_for('ResetMyPasswordView.this_form_get'))

    @action('resetpasswords', lazy_gettext("Reset Password"), "", "fa-lock", multiple=False)
    def resetpasswords(self, item):
        return redirect(url_for('ResetPasswordView.this_form_get', pk=item.id))

    def pre_update(self, item):
        item.changed_on = datetime.datetime.now()
        item.changed_by_fk = g.user.id

    def pre_add(self, item):
        item.password = generate_password_hash(item.password)


class UserStatsChartView(DirectByChartView):
    datamodel = SQLAModel(User)
    chart_title = lazy_gettext('User Statistics')
    label_columns = {'username': lazy_gettext('User Name'),
                     'login_count': lazy_gettext('Login count'),
                     'fail_login_count': lazy_gettext('Failed login count')
    }

    search_columns = UserModelView.search_columns

    definitions = [
        {
            'label': 'Login Count',
            'group': 'username',
            'series': ['login_count']
        },
        {
            'label': 'Failed Login Count',
            'group': 'username',
            'series': ['fail_login_count']
        }

    ]


class RoleModelView(ModelView):
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
    login_template = ''

    invalid_login_message = lazy_gettext('Invalid login. Please try again.')

    title = lazy_gettext('Sign In')

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        pass

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect(self.appbuilder.get_url_for_index)


class RegisterUserDBView(PublicFormView):
    """
        View for Registering a new user, auth db mode
    """
    route_base = '/register'

    email_template = 'appbuilder/general/security/register_mail.html'
    email_subject = lazy_gettext('Account activation')
    activation_template = 'appbuilder/general/security/activation.html'
    form = RegisterUserDBForm
    form_title = lazy_gettext('Fill out the registration form')
    redirect_url = '/'
    error_message = lazy_gettext('Not possible to register you at the moment, try again later')
    message = lazy_gettext('Registration sent to your email')

    def form_get(self, form):
        datamodel_user = SQLAModel(User, self.appbuilder.get_session)
        datamodel_register_user = SQLAModel(RegisterUser, self.appbuilder.get_session)
        if len(form.username.validators) == 1:
            form.username.validators.append(Unique(datamodel_user, 'username'))
            form.username.validators.append(Unique(datamodel_register_user, 'username'))
        if len(form.email.validators) == 2:
            form.email.validators.append(Unique(datamodel_user, 'email'))
            form.email.validators.append(Unique(datamodel_register_user, 'email'))

    @expose('/activation/<string:activation_hash>')
    def activation(self, activation_hash):
        reg = self.appbuilder.get_session.query(RegisterUser).filter(
            RegisterUser.registration_hash == activation_hash).scalar()
        try:
            if not self.appbuilder.sm.add_user(username=reg.username,
                                               email=reg.email,
                                               first_name=reg.first_name,
                                               last_name=reg.last_name,
                                               role=self.appbuilder.sm.get_role_by_name(
                                                       self.appbuilder.sm.auth_user_registration_role),
                                               password=reg.password):
                raise Exception('Could not add user to DB')
            self.appbuilder.get_session.delete(reg)
        except Exception as e:
            log.exception("Add record on user activation error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return redirect(self.appbuilder.get_url_for_index)
        self.appbuilder.get_session.commit()
        return render_template(self.activation_template,
                               username=reg.username,
                               first_name=reg.first_name,
                               last_name=reg.last_name,
                               appbuilder=self.appbuilder)

    def send_email(self, register_user):
        try:
            from flask_mail import Mail, Message
        except:
            log.error("Install Flask-Mail to use User registration")
            return False
        mail = Mail(self.appbuilder.get_app)
        msg = Message()
        msg.subject = self.email_subject
        url = url_for('.activation', _external=True, activation_hash=register_user.registration_hash)
        msg.html = render_template(self.email_template,
                                   url=url,
                                   username=register_user.username,
                                   first_name=register_user.first_name,
                                   last_name=register_user.last_name)
        msg.recipients = [register_user.email]
        try:
            mail.send(msg)
        except Exception as e:
            log.error("Send email exception: {0}".format(str(e)))
            return False
        return True

    def form_post(self, form):
        register_user = RegisterUser()
        register_user.username = form.username.data
        register_user.email = form.email.data
        register_user.first_name = form.first_name.data
        register_user.last_name = form.last_name.data
        register_user.password = generate_password_hash(form.password.data)
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.appbuilder.get_session.add(register_user)
        except Exception as e:
            log.exception("Add record error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return
        if self.send_email(register_user):
            self.appbuilder.get_session.commit()
            flash(as_unicode(self.message), 'info')
        else:
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()


class RegisterUserOIDView(PublicFormView):
    """
        View for Registering a new user, auth db mode
    """
    route_base = '/register'

    email_template = 'appbuilder/general/security/register_mail.html'
    email_subject = lazy_gettext('Account activation')
    activation_template = 'appbuilder/general/security/activation.html'
    form = RegisterUserOIDForm
    form_title = lazy_gettext('Fill out the registration form')
    error_message = lazy_gettext('Not possible to register you at the moment, try again later')
    message = lazy_gettext('Registration sent to your email')
    default_view = 'form_oid_post'

    @expose("/formoidone", methods=['GET','POST'])
    def form_oid_post(self, flag=True):
        if flag:
            self.oid_login_handler(self.form_oid_post, self.appbuilder.sm.oid)
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            print "POST TRY LOGIN"
            return self.appbuilder.sm.oid.try_login(form.openid.data, ask_for=['email', 'fullname'])
        resp = session.pop('oid_resp')
        self._init_vars()
        form = self.form.refresh()
        self.form_get(form)
        form.username.data = resp.email
        form.first_name.data = resp.fullname
        form.email.data = resp.email
        widgets = self._get_edit_widget(form=form)
        #self.update_redirect()
        return self.render_template(self.form_template,
                               title=self.form_title,
                               widgets=widgets,
                               form_action='form',
                               appbuilder=self.appbuilder)


    def oid_login_handler(self, f, oid):
        """
            Hackish method to make use of oid.login_handler decorator.
        """
        print "LOGINHANDLER"
        if request.args.get('openid_complete') != u'yes':
            return f(False)
        consumer = Consumer(SessionWrapper(self), oid.store_factory())
        openid_response = consumer.complete(request.args.to_dict(),
                                            oid.get_current_url())
        if openid_response.status == SUCCESS:
            print "SUCCESS"
            return self.after_login(OpenIDResponse(openid_response, []))
        elif openid_response.status == CANCEL:
            oid.signal_error(u'The request was cancelled')
            return redirect(oid.get_current_url())
        oid.signal_error(u'OpenID authentication error')
        print "REDIRECT"
        return redirect(oid.get_current_url())

    def after_login(self, resp):
        session['oid_resp'] = resp

    def form_get(self, form):
        datamodel_user = SQLAModel(User, self.appbuilder.get_session)
        datamodel_register_user = SQLAModel(RegisterUser, self.appbuilder.get_session)
        if len(form.username.validators) == 1:
            form.username.validators.append(Unique(datamodel_user, 'username'))
            form.username.validators.append(Unique(datamodel_register_user, 'username'))
        if len(form.email.validators) == 2:
            form.email.validators.append(Unique(datamodel_user, 'email'))
            form.email.validators.append(Unique(datamodel_register_user, 'email'))

    @expose('/activation/<string:activation_hash>')
    def activation(self, activation_hash):
        reg = self.appbuilder.get_session.query(RegisterUser).filter(
            RegisterUser.registration_hash == activation_hash).scalar()
        try:
            if not self.appbuilder.sm.add_user(username=reg.username,
                                               email=reg.email,
                                               first_name=reg.first_name,
                                               last_name=reg.last_name,
                                               role=self.appbuilder.sm.get_role_by_name(
                                                       self.appbuilder.sm.auth_user_registration_role),
                                               password=reg.password):
                raise Exception('Could not add user to DB')
            self.appbuilder.get_session.delete(reg)
        except Exception as e:
            log.exception("Add record on user activation error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return redirect(self.appbuilder.get_url_for_index)
        self.appbuilder.get_session.commit()
        return render_template(self.activation_template,
                               username=reg.username,
                               first_name=reg.first_name,
                               last_name=reg.last_name,
                               appbuilder=self.appbuilder)

    def send_email(self, register_user):
        try:
            from flask_mail import Mail, Message
        except:
            log.error("Install Flask-Mail to use User registration")
            return False
        mail = Mail(self.appbuilder.get_app)
        msg = Message()
        msg.subject = self.email_subject
        url = url_for('.activation', _external=True, activation_hash=register_user.registration_hash)
        msg.html = render_template(self.email_template,
                                   url=url,
                                   username=register_user.username,
                                   first_name=register_user.first_name,
                                   last_name=register_user.last_name)
        msg.recipients = [register_user.email]
        try:
            mail.send(msg)
        except Exception as e:
            log.error("Send email exception: {0}".format(str(e)))
            return False
        return True

    def form_post(self, form):
        register_user = RegisterUser()
        register_user.username = form.username.data
        register_user.email = form.email.data
        register_user.first_name = form.first_name.data
        register_user.last_name = form.last_name.data
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.appbuilder.get_session.add(register_user)
        except Exception as e:
            log.exception("Add record error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return
        if self.send_email(register_user):
            self.appbuilder.get_session.commit()
            flash(as_unicode(self.message), 'info')
        else:
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()


class AuthDBView(AuthView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_db(form.username.data, form.password.data)
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)
        return render_template(self.login_template,
                               title=self.title,
                               form=form,
                               appbuilder=self.appbuilder)


class AuthLDAPView(AuthView):
    login_template = 'appbuilder/general/security/login_ldap.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_ldap(form.username.data, form.password.data)
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)
        return render_template(self.login_template,
                               title=self.title,
                               form=form,
                               appbuilder=self.appbuilder)


class AuthOIDView(AuthView):
    login_template = 'appbuilder/general/security/login_oid.html'
    oid_ask_for = ['email']
    oid_ask_for_optional = []

    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):
        if flag:
            self.oid_login_handler(self.login, self.appbuilder.sm.oid)
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return self.appbuilder.sm.oid.try_login(form.openid.data, ask_for=self.oid_ask_for,
                                                    ask_for_optional=self.oid_ask_for_optional)
        return render_template(self.login_template,
                               title=self.title,
                               form=form,
                               providers=self.appbuilder.sm.openid_providers,
                               appbuilder=self.appbuilder
        )

    def oid_login_handler(self, f, oid):
        """
            Hackish method to make use of oid.login_handler decorator.
        """
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
            flash(as_unicode(self.invalid_login_message), 'warning')
            return redirect(self.login_template)
        user = self.appbuilder.sm.auth_user_oid(resp.email)
        if user is None:
            flash(as_unicode(self.invalid_login_message), 'warning')
            return redirect(self.login_template)
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(user, remember=remember_me)
        return redirect(self.appbuilder.get_url_for_index)

