from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Required, Length, validators, EqualTo, PasswordField
from flask.ext.babel import gettext, lazy_gettext

from flask.ext.appbuilder.views import *
from models import *
from ..forms import BS3PasswordFieldWidget
from forms import *


from app import app, db, lm, oid
from flask.ext.appbuilder.models.datamodel import SQLAModel
from config import AUTH_TYPE, APP_NAME, APP_THEME


AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2



#----------------------------- DEFS --------------------------------------
#-------------------------------------------------------------------------

class PermissionGeneralView(GeneralView):
    route_base = '/permissions'
    
    datamodel = SQLAModel(Permission, db.session)

    list_title = lazy_gettext('List Base Permissions')
    show_title = lazy_gettext('Show Base Permission')
    add_title = lazy_gettext('Add Base Permission')
    edit_title = lazy_gettext('Edit Base Permission')

    label_columns = {'name':lazy_gettext('Name')}
    list_columns = ['name']
    show_columns = ['name']
    order_columns = ['name']
    search_columns = ['name']

class ViewMenuGeneralView(GeneralView):
    route_base = '/viewmenus'
    
    datamodel = SQLAModel(ViewMenu, db.session)

    list_title = lazy_gettext('List View Menus')
    show_title = lazy_gettext('Show View Menu')
    add_title = lazy_gettext('Add View Menu')
    edit_title = lazy_gettext('Edit View Menu')

    label_columns = {'name':lazy_gettext('Name')}
    list_columns = ['name']
    show_columns = ['name']
    order_columns = ['name']
    search_columns = ['name']

class PermissionViewGeneralView(GeneralView):
    route_base = '/permissionviews'
    
    datamodel = SQLAModel(PermissionView , db.session)

    list_title = lazy_gettext('List Permissions on Views/Menus')
    show_title = lazy_gettext('Show Permission on Views/Menus')
    add_title = lazy_gettext('Add Permission on Views/Menus')
    edit_title = lazy_gettext('Edit Permission on Views/Menus')

    label_columns = {'permission':lazy_gettext('Permission'), 'view_menu': lazy_gettext('View/Menu')}
    list_columns = ['permission', 'view_menu']
    show_columns = ['permission', 'view_menu']
    order_columns = ['permission', 'view_menu']
    search_columns = ['permission', 'view_menu']


class ResetPasswordView(SimpleFormView):

    route_base = '/resetpassword'
    

    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    form_columns = ['password','conf_password']
    redirect_url = '/'

    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        user = db.session.query(User).get(g.user.id)
        user.password = form.password.data
        db.session.commit()
        flash(unicode(self.message),'info')


class UserGeneralView(GeneralView):
    route_base = '/users'
    datamodel = SQLAModel(User, db.session)
    

    list_title = lazy_gettext('List Users')
    show_title = lazy_gettext('Show User')
    add_title = lazy_gettext('Add User')
    edit_title = lazy_gettext('Edit User')

    label_columns = {'get_full_name':lazy_gettext('Full Name'),
                    'first_name':lazy_gettext('First Name'),
                    'last_name':lazy_gettext('Last Name'),
                    'username':lazy_gettext('User Name'),
                    'password':lazy_gettext('Password'),
                    'active':lazy_gettext('Is Active?'),
                    'email':lazy_gettext('EMail'),
                    'role':lazy_gettext('Role')}
    description_columns = {'first_name':lazy_gettext('Write the user first name or names'),
                    'last_name':lazy_gettext('Write the user last name'),
        'username':lazy_gettext('Username valid for authentication on DB or LDAP, unused for OID auth'),
                    'password':lazy_gettext('Please use a good password policy, this application does not check this for you'),
                    'active':lazy_gettext('Its not a good policy to remove a user, just make it inactive'),
                    'email':lazy_gettext('The users email, this will also be used for OID auth'),
                    'role':lazy_gettext('The user role on the application, this will associate with a list of permissions'),
                    'conf_password':lazy_gettext('Please rewrite the users password to confirm')}
    list_columns = ['get_full_name', 'username', 'email','active', 'role']
    show_columns = ['first_name','last_name','username', 'active', 'email','role']
    order_columns = ['username', 'email']
    search_columns = ['first_name','last_name', 'username', 'email']

    add_columns = ['first_name','last_name','username', 'active', 'email','role']
    edit_columns = ['first_name','last_name','username', 'active', 'email','role']

    user_info_title = lazy_gettext("Your user information")
    lnk_reset_password = lazy_gettext("Reset Password")

    show_additional_links = []

    @expose('/userinfo/')
    def userinfo(self):
        item = g.user

        additional_links = None


        if AUTH_TYPE == AUTH_DB:
            if not self.show_additional_links:
                self.show_additional_links.append(AdditionalLinkItem(self.lnk_reset_password,"/resetpassword/form","lock"))

        widgets = self._get_show_widget(item.id)

        return render_template(self.show_template,
                           title = self.user_info_title,
                           widgets = widgets,
                           baseapp = self.baseapp,
                           )



    def _init_forms(self):
        super(UserGeneralView, self)._init_forms()
        if AUTH_TYPE == AUTH_DB:
            self.add_form.password = PasswordField('Password', 
                                                   description=self.description_columns['password'],
                                                   widget=BS3PasswordFieldWidget())
            self.add_form.conf_password = PasswordField('Confirm Password',
                                            default=self.add_form.password,
                                            description=self.description_columns['conf_password'],
                                            validators=[EqualTo('password',message=u'Passwords must match')],
                                            widget=BS3PasswordFieldWidget())
            if 'password' not in self.add_columns:
                self.add_columns = self.add_columns + ['password', 'conf_password']
        else:
            self.add_form.password = None



class RoleGeneralView(GeneralView):
    route_base = '/roles'
    
    datamodel = SQLAModel(Role, db.session)

    related_views = [PermissionViewGeneralView(), UserGeneralView()]

    list_title = lazy_gettext('List Roles')
    show_title = lazy_gettext('Show Role')
    add_title = lazy_gettext('Add Role')
    edit_title = lazy_gettext('Edit Role')

    label_columns = { 'name':lazy_gettext('Name'),'permissions':lazy_gettext('Permissions') }
    list_columns = ['name','permissions']
    show_columns = ['name','permissions']
    order_columns = ['name']
    search_columns = ['name']



class AuthView(BaseView):

    route_base = ''
    login_db_template = 'appbuilder/general/security/login_db.html'
    login_oid_template = 'appbuilder/general/security/login_oid.html'
    
    invalid_login_message = lazy_gettext('Invalid login. Please try again.')
    
    title = lazy_gettext('Sign In')

    @expose('/login/', methods = ['GET', 'POST'])
    @oid.loginhandler
    def login(self):
        if AUTH_TYPE == AUTH_OID: return self._login_oid()
        if AUTH_TYPE == AUTH_DB: return self._login_db()

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect('/')


    def _login_db(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_db()
        if form.validate_on_submit():
            if form.username.data is None or form.username.data == "":
                flash(unicode(self.invalid_login_message),'warning')
                return redirect('/login')
            user = User.query.filter_by(username = form.username.data, password = form.password.data).first()
            if user is None or (not user.is_active()):
                flash(unicode(self.invalid_login_message),'warning')
                return redirect('/login')
            login_user(user, remember = False)
            return redirect('/')
        return render_template(self.login_db_template,
                                                title = self.title,
                                                form = form,
                                                baseapp = self.baseapp
                                                )

    def _login_oid(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return oid.try_login(form.openid.data, ask_for = ['email'])
        return render_template(self.login_oid_template,
                title = self.title,
                form = form,
                providers = app.config['OPENID_PROVIDERS'],
                baseapp = self.baseapp
                )


def _after_login_oid(resp):
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'),'warning')
        return redirect('appbuilder/general/security/login_oid.html')
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        flash(gettext('Invalid login. Please try again.'),'warning')
        return redirect('appbuilder/general/security/login_oid.html')
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)

    login_user(user, remember = remember_me)
    return redirect('/')


@oid.after_login
def _after_login(resp):
    if AUTH_TYPE == AUTH_OID: return _after_login_oid(resp)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
