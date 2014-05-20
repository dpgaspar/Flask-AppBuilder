import datetime
import logging

from flask import g
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_openid import OpenID
from flask_babelpkg import lazy_gettext as _
from sqlalchemy.engine.reflection import Inspector

from .. import Base
from ..basemanager import BaseManager

from .models import User, Role, PermissionView, Permission, ViewMenu
from .views import AuthDBView, AuthOIDView, ResetMyPasswordView, AuthLDAPView, \
    ResetPasswordView, UserDBModelView, UserLDAPModelView, UserOIDModelView, RoleModelView, \
    PermissionViewModelView, ViewMenuModelView, PermissionModelView, UserStatsChartView

log = logging.getLogger(__name__)

AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2

ADMIN_USER_NAME = 'admin'
ADMIN_USER_PASSWORD = 'general'
ADMIN_USER_EMAIL = 'admin@fab.org'
ADMIN_USER_FIRST_NAME = 'Admin'
ADMIN_USER_LAST_NAME = 'User'


class SecurityManager(BaseManager):
    session = None
    auth_type = 1
    auth_role_admin = ""
    auth_role_public = ""
    auth_view = None
    user_view = None
    auth_ldap_server = ""
    lm = None
    oid = None

    def __init__(self, appbuilder):
        """
            SecurityManager contructor
            param appbuilder:
                F.A.B AppBuilder main object
            """
        super(SecurityManager, self).__init__(appbuilder)
        self.session = appbuilder.get_session
        app = self.appbuilder.get_app
        self.auth_type = self._get_auth_type(app)
        self.auth_role_admin = self._get_auth_role_admin(app)
        self.auth_role_public = self._get_auth_role_public(app)
        if self.auth_type == AUTH_LDAP:
            if 'AUTH_LDAP_SERVER' in app.config:
                self.auth_ldap_server = app.config['AUTH_LDAP_SERVER']
            else:
                raise Exception("No AUTH_LDAP_SERVER defined on config with AUTH_LDAP authentication type.")

        self.lm = LoginManager(app)
        self.lm.login_view = 'login'
        self.oid = OpenID(app)
        self.lm.user_loader(self.load_user)
        self.init_db()

    def register_views(self):
        self.appbuilder.add_view_no_menu(ResetPasswordView())
        self.appbuilder.add_view_no_menu(ResetMyPasswordView())

        if self._get_auth_type(self.appbuilder.get_app) == AUTH_DB:
            self.user_view = UserDBModelView
            self.auth_view = AuthDBView()
        elif self._get_auth_type(self.appbuilder.get_app) == AUTH_LDAP:
            self.user_view = UserLDAPModelView
            self.auth_view = AuthLDAPView()
        else:
            self.user_view = UserOIDModelView
            self.auth_view = AuthOIDView()
            self.oid.after_login_func = self.auth_view.after_login

        self.appbuilder.add_view_no_menu(self.auth_view)

        self.user_view = self.appbuilder.add_view(self.user_view, "List Users",
                                                  icon="fa-user", label=_("List Users"),
                                                  category="Security", category_icon="fa-cogs",
                                                  category_label=_('Security'))

        role_view = self.appbuilder.add_view(RoleModelView, "List Roles", icon="fa-group", label=_('List Roles'),
                                             category="Security", category_icon="fa-cogs")
        role_view.related_views = [self.user_view.__class__]
        self.appbuilder.add_view(UserStatsChartView,
                                 "User's Statistics", icon="fa-bar-chart-o", label=_("User's Statistics"),
                                 category="Security")
        self.appbuilder.menu.add_separator("Security")
        self.appbuilder.add_view(PermissionModelView,
                                 "Base Permissions", icon="fa-lock",
                                 label=_("Base Permissions"), category="Security")
        self.appbuilder.add_view(ViewMenuModelView,
                                 "Views/Menus", icon="fa-list-alt",
                                 label=_('Views/Menus'), category="Security")
        self.appbuilder.add_view(PermissionViewModelView,
                                 "Permission on Views/Menus", icon="fa-link",
                                 label=_('Permission on Views/Menus'), category="Security")


    def load_user(self, pk):
        return self.get_user_by_id(int(pk))

    @staticmethod
    def before_request():
        g.user = current_user

    def _migrate_db(self):
        """
            Migrate from 0.8 to 0.9, change GeneralView to ModelView
            on ViewMenus
        """
        sec_view_prefixes = ['Permission', 'ViewMenu', 'PermissionView',
                             'UserOID', 'UserLDAP', 'UserDB',
                             'Role']
        sec_view_old_sufix = 'GeneralView'
        sec_view_new_sufix = 'ModelView'
        for sec_view_prefix in sec_view_prefixes:
            sec_view = self._find_view_menu('{0}{1}'.format(sec_view_prefix, sec_view_old_sufix))
            if sec_view:
                try:
                    log.info("Migrate from 0.8 to 0.9 Changing {0}{1}".format(sec_view_prefix, sec_view_old_sufix))
                    sec_view.name = '{0}{1}'.format(sec_view_prefix, sec_view_new_sufix)
                    self.session.merge(sec_view)
                    self.session.commit()
                except Exception as e:
                    log.error("Update ViewMenu error: {0}".format(str(e)))
                    self.session.rollback()


    def init_db(self):
        try:
            engine = self.session.get_bind(mapper=None, clause=None)
            inspector = Inspector.from_engine(engine)
            if 'ab_user' not in inspector.get_table_names():
                log.info("Security DB not found Creating all Models from Base")
                Base.metadata.create_all(engine)
                log.info("Security DB Created")
            else:
                self._migrate_db()
            if not self.session.query(Role).filter_by(name=self.auth_role_admin).first():
                role = Role()
                role.name = self.auth_role_admin
                self.session.add(role)
                self.session.commit()
                log.info("Inserted Role for public access %s" % (self.auth_role_admin))
            if not self.session.query(Role).filter_by(name=self.auth_role_public).first():
                role = Role()
                role.name = self.auth_role_public
                self.session.add(role)
                self.session.commit()
                log.info("Inserted Role for public access %s" % (self.auth_role_public))
            if not self.session.query(User).all():
                user = User()
                user.first_name = ADMIN_USER_FIRST_NAME
                user.last_name = ADMIN_USER_LAST_NAME
                user.username = ADMIN_USER_NAME
                user.password = generate_password_hash(ADMIN_USER_PASSWORD)
                user.email = ADMIN_USER_EMAIL
                user.active = True
                user.role = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
                self.session.add(user)
                self.session.commit()
                log.info("Inserted initial Admin user")
                log.info("Login using {0}/{1}".format(ADMIN_USER_NAME, ADMIN_USER_PASSWORD))
        except Exception as e:
            log.error(
                "DB Creation and initialization failed, if just upgraded to 0.7.X you must migrate the DB. {0}".format(
                    str(e)))


    """
    ----------------------------------------
        AUTHENTICATION METHODS
    ----------------------------------------
    """

    def auth_user_db(self, username, password):
        """
            Method for authenticating user, auth db style

            :param username:
                The username
            :param password:
                The password, will be tested against hashed password on db
        """
        if username is None or username == "":
            return None
        user = self.session.query(User).filter_by(username=username).first()
        if user is None or (not user.is_active()):
            return None
        elif check_password_hash(user.password, password):
            self._update_user_auth_stat(user, True)
            return user
        else:
            self._update_user_auth_stat(user, False)
            return None

    def auth_user_ldap(self, username, password):
        """
            Method for authenticating user, auth LDAP style.
            depends on ldap module that is not mandatory requirement
            for F.A.B.

            :param username:
                The username
            :param password:
                The password
        """
        if username is None or username == "":
            return None
        user = self.session.query(User).filter_by(username=username).first()
        if user is None or (not user.is_active()):
            return None
        else:
            try:
                import ldap
            except:
                raise Exception("No ldap library for python.")
            try:
                con = ldap.initialize(self.auth_ldap_server)
                con.set_option(ldap.OPT_REFERRALS, 0)
                try:
                    con.bind_s(username, password)
                    self._update_user_auth_stat(user)
                    return user
                except ldap.INVALID_CREDENTIALS:
                    self._update_user_auth_stat(user, False)
                    return None
            except ldap.LDAPError as e:
                if type(e.message) == dict and 'desc' in e.message:
                    log.error("LDAP Error {0}".format(e.message['desc']))
                    return None
                else:
                    log.error(e)
                    return None

    def auth_user_oid(self, email):
        """
            OpenID user Authentication

            :type self: User model
        """
        user = self.session.query(User).filter_by(email=email).first()
        if user is None:
            self._update_user_auth_stat(user, False)
            return None
        elif not user.is_active():
            return None
        else:
            self._update_user_auth_stat(user)
            return user

    def _update_user_auth_stat(self, user, success=True):
        """
            Update authentication successful to user.

            :param user:
                The authenticated user model
        """
        try:
            if not user.login_count:
                user.login_count = 0
            elif not user.fail_login_count:
                user.fail_login_count = 0
            if success:
                user.login_count += 1
                user.fail_login_count = 0
            else:
                user.fail_login_count += 1
            user.last_login = datetime.datetime.now()
            self.session.merge(user)
            self.session.commit()
        except Exception as e:
            log.error("Update user login stat: {0}".format(str(e)))
            self.session.rollback()


    def reset_password(self, userid, password):
        try:
            user = self.get_user_by_id(userid)
            user.password = generate_password_hash(password)
            self.session.commit()
        except Exception as e:
            log.error("Reset password: {0}".format(str(e)))
            self.session.rollback()

    def get_user_by_id(self, pk):
        return self.session.query(User).get(pk)

    def _get_auth_type(self, app):
        if 'AUTH_TYPE' in app.config:
            return app.config['AUTH_TYPE']
        else:
            return AUTH_DB

    def _get_auth_role_admin(self, app):
        if 'AUTH_ROLE_ADMIN' in app.config:
            return app.config['AUTH_ROLE_ADMIN']
        else:
            return 'Admin'

    def _get_auth_role_public(self, app):
        """
            To retrive the name of the public role
        """
        if 'AUTH_ROLE_PUBLIC' in app.config:
            return app.config['AUTH_ROLE_PUBLIC']
        else:
            return 'Public'


    """
        ----------------------------------------
            PERMISSION ACCESS CHECK
        ----------------------------------------
    """

    def is_item_public(self, permission_name, view_name):
        """
            Check if view has public permissions
    
            :param permission_name:
                the permission: can_show, can_edit...
            :param view_name:
                the name of the class view (child of BaseView)
        """

        role = self.session.query(Role).filter_by(name=self.auth_role_public).first()
        lst = role.permissions
        if lst:
            for i in lst:
                if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else:
            return False


    def has_view_access(self, user, permission_name, view_name):
        lst = user.role.permissions
        if lst:
            for i in lst:
                if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else:
            return False


    def has_access(self, permission_name, view_name):
        """
            Check if current user or public has access to view or menu
        """
        if current_user.is_authenticated():
            if self.has_view_access(g.user, permission_name, view_name):
                return True
            else:
                return False
        else:
            if self.is_item_public(permission_name, view_name):
                return True
            else:
                return False
        return False


    """
        ----------------------------------------
            PERMISSION MANAGEMENT
        ----------------------------------------
    """

    def _find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        return self.session.query(Permission).filter_by(name=name).first()


    def _add_permission(self, name):
        """
            Adds a permission to the backend, model permission
            
            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self._find_permission(name)
        if perm is None:
            try:
                perm = Permission()
                perm.name = name
                self.session.add(perm)
                self.session.commit()
                return perm
            except Exception as e:
                log.error("Add Permission: {0}".format(str(e)))
                self.session.rollback()
        return perm

    def _del_permission(self, name):
        """
            Deletes a permission from the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self._find_permission(name)
        if perm:
            try:
                self.session.delete(perm)
                self.session.commit()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))
                self.session.rollback()

    #----------------------------------------------
    #       PERMITIVES VIEW MENU
    #----------------------------------------------
    def _find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        return self.session.query(ViewMenu).filter_by(name=name).first()

    def _add_view_menu(self, name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        view_menu = self._find_view_menu(name)
        if view_menu is None:
            try:
                view_menu = ViewMenu()
                view_menu.name = name
                self.session.add(view_menu)
                self.session.commit()
                return view_menu
            except Exception as e:
                log.error("Add View Menu Error: {0}".format(str(e)))
                self.session.rollback()
        return view_menu

    def _del_view_menu(self, name):
        """
            Deletes a ViewMenu from the backend

            :param name:
                name of the ViewMenu
        """
        obj = self._find_view_menu(name)
        if obj:
            try:
                self.session.delete(obj)
                self.session.commit()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))
                self.session.rollback()

    #----------------------------------------------
    #          PERMISSION VIEW MENU
    #----------------------------------------------
    def _find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        permission = self._find_permission(permission_name)
        view_menu = self._find_view_menu(view_menu_name)
        return self.session.query(PermissionView).filter_by(permission=permission, view_menu=view_menu).first()


    def _add_permission_view_menu(self, permission_name, view_menu_name):
        """
            Adds a permission on a view or menu to the backend
            
            :param permission_name:
                name of the permission to add: 'can_add','can_edit' etc...
            :param view_menu_name:
                name of the view menu to add
        """
        vm = self._add_view_menu(view_menu_name)
        perm = self._add_permission(permission_name)
        pv = PermissionView()
        pv.view_menu_id, pv.permission_id = vm.id, perm.id
        try:
            self.session.add(pv)
            self.session.commit()
            log.info("Created Permission View: %s" % (str(pv)))
            return pv
        except Exception as e:
            log.error("Creation of Permission View Error: {0}".format(str(e)))
            self.session.rollback()


    def _del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            pv = self._find_permission_view_menu(permission_name, view_menu_name)
            # delete permission on view
            self.session.delete(pv)
            self.session.commit()
            # if no more permission on permission view, delete permission
            pv = self.session.query(PermissionView).filter_by(permission=pv.permission).all()
            if not pv:
                self._del_permission(pv.permission.name)
            log.info("Removed Permission View: %s" % (str(permission_name)))
        except Exception as e:
            log.error("Remove Permission from View Error: {0}".format(str(e)))
            self.session.rollback()


    def _find_permission_on_views(self, lst, item):
        for i in lst:
            if i.permission.name == item:
                return True
        return False

    def _find_permission_view(self, lst, permission, view_menu):
        for i in lst:
            if i.permission.name == permission and i.view_menu.name == view_menu:
                return True
        return False

    def add_permission_role(self, role, perm_view):
        """
            Add permission-ViewMenu object to Role
            
            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        if perm_view not in role.permissions:
            try:
                role.permissions.append(perm_view)
                self.session.merge(role)
                self.session.commit()
                log.info("Added Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Add Permission to Role Error: {0}".format(str(e)))
                self.session.rollback()


    def del_permission_role(self, role, perm_view):
        """
            Remove permission-ViewMenu object to Role
            
            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        if perm_view in role.permissions:
            try:
                role.permissions.remove(perm_view)
                self.session.merge(role)
                self.session.commit()
                log.info("Removed Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Remove Permission to Role Error: {0}".format(str(e)))
                self.session.rollback()


    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend

            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        view_menu_db = self._add_view_menu(view_menu)
        perm_views = self.session.query(PermissionView).filter_by(view_menu_id=view_menu_db.id).all()

        if not perm_views:
            # No permissions yet on this view
            for permission in base_permissions:
                pv = self._add_permission_view_menu(permission, view_menu)
                role_admin = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
                self.add_permission_role(role_admin, pv)
        else:
            # Permissions on this view exist but....
            role_admin = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
            for permission in base_permissions:
                # Check if base view permissions exist
                if not self._find_permission_on_views(perm_views, permission):
                    pv = self._add_permission_view_menu(permission, view_menu)
                    self.add_permission_role(role_admin, pv)
            for perm_view in perm_views:
                if perm_view.permission.name not in base_permissions:
                    # perm to delete
                    roles = self.session.query(Role).all()
                    perm = self._find_permission(perm_view.permission.name)
                    # del permission from all roles
                    for role in roles:
                        self.del_permission_role(role, perm)
                    self._del_permission_view_menu(perm_view.permission.name, view_menu)
                elif perm_view not in role_admin.permissions:
                    # Role Admin must have all permissions
                    self.add_permission_role(role_admin, perm_view)


    def add_permissions_menu(self, view_menu_name):
        """
            Adds menu_access to menu on permission_view_menu

            :param view_menu_name:
                The menu name
        """
        self._add_view_menu(view_menu_name)
        pv = self._find_permission_view_menu('menu_access', view_menu_name)
        if not pv:
            pv = self._add_permission_view_menu('menu_access', view_menu_name)
            role_admin = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
            self.add_permission_role(role_admin, pv)


    def security_cleanup(self, baseviews, menus):
        viewsmenus = self.session.query(ViewMenu).all()
        roles = self.session.query(Role).all()
        for viewmenu in viewsmenus:
            found = False
            for baseview in baseviews:
                if viewmenu.name == baseview.__class__.__name__:
                    found = True
                    break
            if menus.find(viewmenu.name):
                found = True
            if not found:
                permissions = self.session.query(PermissionView).filter_by(view_menu_id=viewmenu.id).all()
                for permission in permissions:
                    for role in roles:
                        self.del_permission_role(role, permission)
                    self._del_permission_view_menu(permission.permission.name, viewmenu.name)
                self.session.delete(viewmenu)
                self.session.commit()

