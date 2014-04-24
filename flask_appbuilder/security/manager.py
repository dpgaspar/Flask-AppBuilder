import datetime
import logging

from flask import g
from flask_login import current_user
from sqlalchemy import MetaData, Table
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_openid import OpenID
from flask_babelpkg import lazy_gettext as _

from flask_appbuilder import Base

from models import User, Role, PermissionView, Permission, ViewMenu, \
    assoc_permissionview_role
from views import AuthDBView, AuthOIDView, ResetMyPasswordView, AuthLDAPView, \
    ResetPasswordView, UserDBGeneralView, UserLDAPGeneralView, UserOIDGeneralView, RoleGeneralView, \
    PermissionViewGeneralView, ViewMenuGeneralView, PermissionGeneralView, UserStatsChartView


log = logging.getLogger(__name__)

AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2


class SecurityManager(object):
    session = None
    auth_type = 1
    auth_role_admin = ""
    auth_role_public = ""
    auth_view = None
    user_view = None
    auth_ldap_server = ""
    lm = None
    oid = None

    def __init__(self, app, session):
        """
            SecurityManager contructor
            param app:
                The Flask app object
            param session:
                the database session for security tables, passed to BaseApp
        """
        self.session = session
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

    def register_views(self, baseapp):
        baseapp.add_view_no_menu(ResetPasswordView())
        baseapp.add_view_no_menu(ResetMyPasswordView())

        if self._get_auth_type(baseapp.app) == AUTH_DB:
            self.user_view = baseapp._init_view_session(UserDBGeneralView)
            self.auth_view = AuthDBView()
        elif self._get_auth_type(baseapp.app) == AUTH_LDAP:
            self.user_view = baseapp._init_view_session(UserLDAPGeneralView)
            self.auth_view = AuthLDAPView()
        else:
            self.user_view = baseapp._init_view_session(UserOIDGeneralView)
            self.auth_view = AuthOIDView()
            self.oid.after_login_func = self.auth_view.after_login

        baseapp.add_view_no_menu(self.auth_view)

        baseapp.add_view(self.user_view, "List Users"
                         , icon="fa-user", label=_("List Users"),
                         category="Security", category_icon="fa-cogs", category_label=_('Security'))

        role_view = baseapp._init_view_session(RoleGeneralView)
        baseapp.add_view(role_view, "List Roles", icon="fa-group", label=_('List Roles'),
                         category="Security", category_icon="fa-cogs")
        role_view.related_views = [self.user_view.__class__]
        baseapp.add_view(baseapp._init_view_session(UserStatsChartView),
                         "User's Statistics", icon="fa-bar-chart-o", label=_("User's Statistics"),
                         category="Security")
        baseapp.menu.add_separator("Security")
        baseapp.add_view(baseapp._init_view_session(PermissionViewGeneralView),
                         "Base Permissions", icon="fa-lock",
                         label=_("Base Permissions"), category="Security")
        baseapp.add_view(baseapp._init_view_session(ViewMenuGeneralView),
                         "Views/Menus", icon="fa-list-alt",
                         label=_('Views/Menus'), category="Security")
        baseapp.add_view(baseapp._init_view_session(PermissionGeneralView), "Permission on Views/Menus",
                         icon="fa-link", label=_('Permission on Views/Menus'),
                         category="Security")


    def load_user(self, pk):
        return self.get_user_by_id(int(pk))

    @staticmethod
    def before_request():
        g.user = current_user

    def migrate_get_new_obj(self, old_obj, new_obj):
        for col in old_obj.keys():
            setattr(new_obj, col, getattr(old_obj, col))
        return new_obj

    def migrate_obj(self, old_table, new_class):
        old_objs = self.session.query(old_table).all()
        for old_obj in old_objs:
            new_obj = self.migrate_get_new_obj(old_obj, new_class())
            self.session.add(new_obj)
            self.session.commit()

    def quick_mapper(self, table):
        Base = declarative_base()

        class GenericMapper(Base):
            __table__ = table

        return GenericMapper


    def migrate_db(self):
        """
            Migrate security tables from Flask-AppBuilder 0.2.X to 0.3.X
        """
        engine = self.session.get_bind(mapper=None, clause=None)
        inspector = Inspector.from_engine(engine)
        if 'user' in inspector.get_table_names() and 'role' in inspector.get_table_names() and 'permission' in inspector.get_table_names():
            print "Found previous security tables, migrating..."

            metadata = MetaData(engine)

            old_user = Table('user', metadata, autoload=True)
            old_role = Table('role', metadata, autoload=True)
            old_permission = Table('permission', metadata, autoload=True)
            old_permission_view = Table('permission_view', metadata, autoload=True)
            old_view_menu = Table('view_menu', metadata, autoload=True)
            old_permission_view_role = Table('permission_view_role', metadata, autoload=True)

            print "Migrating Views and Menus"
            self.migrate_obj(old_view_menu, ViewMenu)

            print "Migrating Permissions"
            self.migrate_obj(old_permission, Permission)

            print "Migrating Permissions on Views"
            self.migrate_obj(old_permission_view, PermissionView)

            print "Migrating Roles"
            self.migrate_obj(old_role, Role)

            print "Migrating Roles to Permissions on Views"
            self.migrate_obj(old_permission_view_role, self.quick_mapper(assoc_permissionview_role))

            print "Migrating Users"
            self.migrate_obj(old_user, User)


    def init_db(self):
        try:
            engine = self.session.get_bind(mapper=None, clause=None)

            inspector = Inspector.from_engine(engine)
            if 'ab_user' not in inspector.get_table_names():
                log.info("Security DB not found Creating")
                Base.metadata.create_all(engine)
                log.info("Security DB Created")
                self.migrate_db()
            if self.session.query(Role).filter_by(name=self.auth_role_admin).first() is None:
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
                user.first_name = 'Admin'
                user.last_name = 'User'
                user.username = 'admin'
                user.password = generate_password_hash('general')
                user.email = 'admin@fab.org'
                user.active = True
                user.role = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
                self.session.add(user)
                self.session.commit()
                log.info("Inserted initial Admin user")
                log.info("Login using Admin/general")
        except Exception as e:
            log.error("DB Creation and initialization failed, if just upgraded to 0.7.X you must migrate the DB. {0}".format(str(e)))


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
            except ldap.LDAPError, e:
                if type(e.message) == dict and e.message.has_key('desc'):
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

    def _add_permission(self, name):
        """
            Adds a permission to the backend, model permission
            
            :param name:
                name of the permission to add: 'can_add','can_edit' etc...
        """
        perm = self.session.query(Permission).filter_by(name=name).first()
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


    def _add_view_menu(self, view_name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        view_menu = self.session.query(ViewMenu).filter_by(name=view_name).first()
        if view_menu is None:
            try:
                view_menu = ViewMenu()
                view_menu.name = view_name
                self.session.add(view_menu)
                self.session.commit()
                return view_menu
            except Exception as e:
                log.error("Add View Menu Error: {0}".format(str(e)))
                self.session.rollback()
        return view_menu

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
            log.info("Added Permission View %s" % (str(pv)))
            return pv
        except Exception as e:
            log.error("Add Permission to View Error: {0}".format(str(e)))
            self.session.rollback()


    def _del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            perm = self.session.query(Permission).filter_by(name=permission_name).first()
            vm = self.session.query(ViewMenu).filter_by(name=view_menu_name).first()
            pv = self.session.query(PermissionView).filter_by(permission=perm, view_menu=vm).first()
            # delete permission on view
            self.session.delete(pv)
            self.session.commit()
            # if last permission delete permission
            pv = self.session.query(PermissionView).filter_by(permission=perm).all()
            if not pv:
                self.session.delete(perm)
                self.session.commit()
            log.info("Removed Permission View %s" % (str(permission_name)))
        except Exception as e:
            log.error("Del Permission from View Error: {0}".format(str(e)))
            self.session.rollback()


    def _find_permission(self, lst, item):
        for i in lst:
            if i.permission.name == item:
                return True
        return False

    def _find_permission_view(self, lst, permission, view_menu):
        for i in lst:
            if i.permission.name == permission and i.view_menu.name == view_menu:
                return True
        return False

    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend
            
            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        view_menu_db = self.session.query(ViewMenu).filter_by(name=view_menu).first()
        if view_menu_db is None:
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
                if not self._find_permission(perm_views, permission):
                    pv = self._add_permission_view_menu(permission, view_menu)
                    self.add_permission_role(role_admin, pv)
            for perm_view in perm_views:
                if perm_view.permission.name not in base_permissions:
                    # perm to delete
                    roles = self.session.query(Role).all()
                    perm = self.session.query(Permission).filter_by(name=perm_view.permission.name).first()
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
        view_menu = self.session.query(ViewMenu).filter_by(name=view_menu_name).first()
        if view_menu is None:
            view_menu = self._add_view_menu(view_menu_name)
        lst = self.session.query(PermissionView).filter_by(view_menu_id=view_menu.id).all()
        if not lst:
            pv = self._add_permission_view_menu('menu_access', view_menu_name)
            role_admin = self.session.query(Role).filter_by(name=self.auth_role_admin).first()
            self.add_permission_role(role_admin, pv)

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
                log.error("Del Permission to Role Error: {0}".format(str(e)))
                self.session.rollback()
