import datetime
import logging

from flask import g
from flask_login import current_user
from flask_babelpkg import lazy_gettext as _
from sqlalchemy import func
from sqlalchemy.engine.reflection import Inspector

from ...models.sqla import Base
from .models import User, Role, PermissionView, Permission, ViewMenu
from .views import AuthDBView, AuthOIDView, ResetMyPasswordView, AuthLDAPView, AuthOAuthView, AuthRemoteUserView, \
    ResetPasswordView, UserDBModelView, UserLDAPModelView, UserOIDModelView, UserOAuthModelView, UserRemoteUserModelView, \
    RoleModelView, PermissionViewModelView, ViewMenuModelView, PermissionModelView, UserStatsChartView
from .registerviews import RegisterUserDBView, RegisterUserOIDView

log = logging.getLogger(__name__)

# Constants for supported authentication types
from ..manager import AUTH_OAUTH, AUTH_OID, AUTH_DB, AUTH_LDAP, AUTH_REMOTE_USER, ADMIN_USER_EMAIL, \
    ADMIN_USER_FIRST_NAME, ADMIN_USER_LAST_NAME, ADMIN_USER_NAME, ADMIN_USER_PASSWORD, BaseSecurityManager


class SecurityManager(BaseSecurityManager):
    """
        Responsible for authentication, registering security views,
        role and permission auto management

        If you want to change anything just inherit and override, then
        pass your own security manager to AppBuilder.
    """
    auth_view = None
    """ The obj instance for authentication view """
    user_view = None
    """ The obj instance for user view """
    registeruser_view = None
    """ The obj instance for registering user view """
    lm = None
    """ Flask-Login LoginManager """
    oid = None
    """ Flask-OpenID OpenID """
    oauth = None
    """ Flask-OAuth """
    oauth_handler = None
    """ OAuth handler, you can use this to use OAuth API's on your app """

    userdbmodelview = UserDBModelView
    """ Override if you want your own user db view """
    userldapmodelview = UserLDAPModelView
    """ Override if you want your own user ldap view """
    useroidmodelview = UserOIDModelView
    """ Override if you want your own user OID view """
    useroauthmodelview = UserOAuthModelView
    """ Override if you want your own user OAuth view """
    userremoteusermodelview = UserRemoteUserModelView
    """ Override if you want your own user REMOTE_USER view """
    authdbview = AuthDBView
    """ Override if you want your own Authentication DB view """
    authldapview = AuthLDAPView
    """ Override if you want your own Authentication LDAP view """
    authoidview = AuthOIDView
    """ Override if you want your own Authentication OID view """
    authoauthview = AuthOAuthView
    """ Override if you want your own Authentication OAuth view """
    authremoteuserview = AuthRemoteUserView
    """ Override if you want your own Authentication OAuth view """
    registeruserdbview = RegisterUserDBView
    """ Override if you want your own register user db view """
    registeruseroidview = RegisterUserOIDView
    """ Override if you want your own register user db view """


    def __init__(self, appbuilder):
        """
            SecurityManager contructor
            param appbuilder:
                F.A.B AppBuilder main object
            """
        super(SecurityManager, self).__init__(appbuilder)
        self.create_db()

    @property
    def get_session(self):
        return self.appbuilder.get_session

    def register_views(self):
        self.appbuilder.add_view_no_menu(ResetPasswordView())
        self.appbuilder.add_view_no_menu(ResetMyPasswordView())

        if self.auth_type == AUTH_DB:
            self.user_view = self.userdbmodelview
            self.auth_view = self.authdbview()
            if self.auth_user_registration:
                self.registeruser_view = self.registeruserdbview()
                self.appbuilder.add_view_no_menu(self.registeruser_view)
        elif self.auth_type == AUTH_LDAP:
            self.user_view = self.userldapmodelview
            self.auth_view = self.authldapview()
        elif self.auth_type == AUTH_OAUTH:
            self.user_view = self.useroauthmodelview
            self.auth_view = self.authoauthview()
        elif self.auth_type == AUTH_REMOTE_USER:
            self.user_view = self.userremoteusermodelview
            self.auth_view = self.authremoteuserview()
        else:
            self.user_view = self.useroidmodelview
            self.auth_view = self.authoidview()
            if self.auth_user_registration:
                self.registeruser_view = self.registeruseroidview()
                self.appbuilder.add_view_no_menu(self.registeruser_view)

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

    def create_db(self):
        try:
            engine = self.get_session.get_bind(mapper=None, clause=None)
            inspector = Inspector.from_engine(engine)
            if 'ab_user' not in inspector.get_table_names():
                log.info("Security DB not found Creating all Models from Base")
                Base.metadata.create_all(engine)
                log.info("Security DB Created")
            super(SecurityManager, self).create_db()
        except Exception as e:
            log.error(
                "DB Creation and initialization failed, if just upgraded to 0.7.X you must migrate the DB. {0}".format(
                    str(e)))

    def find_user(self, username=None, email=None):
        if username:
            return self.get_session.query(User).filter(func.lower(User.username) == func.lower(username)).first()
        elif email:
            return self.get_session.query(User).filter_by(email=email).first()
        
    def add_user(self, username, first_name, last_name, email, role, password=''):
        """
            Generic function to create user
        """
        try:
            user = User()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            user.role = role
            user.password = password
            self.get_session.add(user)
            self.get_session.commit()
            log.info("Added user %s to user list." % username)
            return user
        except Exception as e:
            log.error(
                "Error adding new user to database. {0}".format(
                    str(e)))
            return False

    def count_users(self):
        return self.get_session.query(func.count('*')).select_from(User).scalar()

    def update_user(self, user):
        try:
            self.get_session.merge(user)
            self.get_session.commit()
        except Exception as e:
            log.error(
                "Error updating user to database. {0}".format(
                    str(e)))
            self.get_session.rollback()
            return False

    def get_user_by_id(self, pk):
        return self.get_session.query(User).get(pk)


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
        permissions = self.get_public_permissions()
        if permissions:
            for i in permissions:
                if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else:
            return False

    def _has_view_access(self, user, permission_name, view_name):
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
            if self._has_view_access(g.user, permission_name, view_name):
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
    def add_role(self, name):
        role = self.find_role(name)
        if role is None:
            try:
                role = Role()
                role.name = name
                self.get_session.add(role)
                self.get_session.commit()
                return role
            except Exception as e:
                log.error("Add Role: {0}".format(str(e)))
                self.get_session.rollback()
        return role

    def find_role(self, name):
        return self.get_session.query(Role).filter_by(name=name).first()

    def get_public_permissions(self):
        role = self.get_session.query(Role).filter_by(name=self.auth_role_public).first()
        return role.permissions

    def _find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        return self.get_session.query(Permission).filter_by(name=name).first()


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
                self.get_session.add(perm)
                self.get_session.commit()
                return perm
            except Exception as e:
                log.error("Add Permission: {0}".format(str(e)))
                self.get_session.rollback()
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
                self.get_session.delete(perm)
                self.get_session.commit()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))
                self.get_session.rollback()

    # ----------------------------------------------
    #       PRIMITIVES VIEW MENU
    #----------------------------------------------
    def _find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        return self.get_session.query(ViewMenu).filter_by(name=name).first()

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
                self.get_session.add(view_menu)
                self.get_session.commit()
                return view_menu
            except Exception as e:
                log.error("Add View Menu Error: {0}".format(str(e)))
                self.get_session.rollback()
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
                self.get_session.delete(obj)
                self.get_session.commit()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))
                self.get_session.rollback()

    #----------------------------------------------
    #          PERMISSION VIEW MENU
    #----------------------------------------------
    def _find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        permission = self._find_permission(permission_name)
        view_menu = self._find_view_menu(view_menu_name)
        return self.get_session.query(PermissionView).filter_by(permission=permission, view_menu=view_menu).first()


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
            self.get_session.add(pv)
            self.get_session.commit()
            log.info("Created Permission View: %s" % (str(pv)))
            return pv
        except Exception as e:
            log.error("Creation of Permission View Error: {0}".format(str(e)))
            self.get_session.rollback()


    def _del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            pv = self._find_permission_view_menu(permission_name, view_menu_name)
            # delete permission on view
            self.get_session.delete(pv)
            self.get_session.commit()
            # if no more permission on permission view, delete permission
            pv = self.get_session.query(PermissionView).filter_by(permission=pv.permission).all()
            if not pv:
                self._del_permission(pv.permission.name)
            log.info("Removed Permission View: %s" % (str(permission_name)))
        except Exception as e:
            log.error("Remove Permission from View Error: {0}".format(str(e)))
            self.get_session.rollback()


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
                self.get_session.merge(role)
                self.get_session.commit()
                log.info("Added Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Add Permission to Role Error: {0}".format(str(e)))
                self.get_session.rollback()


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
                self.get_session.merge(role)
                self.get_session.commit()
                log.info("Removed Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Remove Permission to Role Error: {0}".format(str(e)))
                self.get_session.rollback()


    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend

            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        view_menu_db = self._add_view_menu(view_menu)
        perm_views = self.get_session.query(PermissionView).filter_by(view_menu_id=view_menu_db.id).all()

        if not perm_views:
            # No permissions yet on this view
            for permission in base_permissions:
                pv = self._add_permission_view_menu(permission, view_menu)
                role_admin = self.get_session.query(Role).filter_by(name=self.auth_role_admin).first()
                self.add_permission_role(role_admin, pv)
        else:
            # Permissions on this view exist but....
            role_admin = self.get_session.query(Role).filter_by(name=self.auth_role_admin).first()
            for permission in base_permissions:
                # Check if base view permissions exist
                if not self._find_permission_on_views(perm_views, permission):
                    pv = self._add_permission_view_menu(permission, view_menu)
                    self.add_permission_role(role_admin, pv)
            for perm_view in perm_views:
                if perm_view.permission.name not in base_permissions:
                    # perm to delete
                    roles = self.get_session.query(Role).all()
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
            role_admin = self.get_session.query(Role).filter_by(name=self.auth_role_admin).first()
            self.add_permission_role(role_admin, pv)

    def security_cleanup(self, baseviews, menus):
        """
            Will cleanup from the database all unused permissions

            :param baseviews: A list of BaseViews class
            :param menus: Menu class
        """
        viewsmenus = self.get_session.query(ViewMenu).all()
        roles = self.get_session.query(Role).all()
        for viewmenu in viewsmenus:
            found = False
            for baseview in baseviews:
                if viewmenu.name == baseview.__class__.__name__:
                    found = True
                    break
            if menus.find(viewmenu.name):
                found = True
            if not found:
                permissions = self.get_session.query(PermissionView).filter_by(view_menu_id=viewmenu.id).all()
                for permission in permissions:
                    for role in roles:
                        self.del_permission_role(role, permission)
                    self._del_permission_view_menu(permission.permission.name, viewmenu.name)
                self.get_session.delete(viewmenu)
                self.get_session.commit()

