import datetime
import logging

from flask import g
from flask_login import current_user

from .models import User, Role, PermissionView, Permission, ViewMenu
from .views import AuthDBView, AuthOIDView, ResetMyPasswordView, AuthLDAPView, AuthOAuthView, AuthRemoteUserView, \
    ResetPasswordView, UserDBModelView, UserLDAPModelView, UserOIDModelView, UserOAuthModelView, UserRemoteUserModelView, \
    RoleModelView, PermissionViewModelView, ViewMenuModelView, PermissionModelView, UserStatsChartView
#from .registerviews import RegisterUserDBView, RegisterUserOIDView
from ..manager import BaseSecurityManager

log = logging.getLogger(__name__)



class SecurityManager(BaseSecurityManager):
    """
        Responsible for authentication, registering security views,
        role and permission auto management

        If you want to change anything just inherit and override, then
        pass your own security manager to AppBuilder.
    """
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
    #registeruserdbview = RegisterUserDBView
    """ Override if you want your own register user db view """
    #registeruseroidview = RegisterUserOIDView
    """ Override if you want your own register user db view """
    resetmypasswordview = ResetMyPasswordView
    """ Override if you want your own reset my password view """
    resetpasswordview = ResetPasswordView
    """ Override if you want your own reset password view """
    rolemodelview = RoleModelView
    permissionmodelview = PermissionModelView
    userstatschartview = UserStatsChartView
    viewmenumodelview = ViewMenuModelView
    permissionviewmodelview = PermissionViewModelView

    def __init__(self, appbuilder):
        """
            SecurityManager contructor
            param appbuilder:
                F.A.B AppBuilder main object
            """
        super(SecurityManager, self).__init__(appbuilder)
        self.create_db()

    def find_user(self, username=None, email=None):
        if username:
            return User.objects(username=username).first()
        elif email:
            return User.objects(email=email).first()
        
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
            user.roles.append(role)
            user.password = password
            user.save()
            log.info("Added user %s to user list." % username)
            return user
        except Exception as e:
            log.error(
                "Error adding new user to database. {0}".format(
                    str(e)))
            return False

    def count_users(self):
        return len(User.objects)

    def update_user(self, user):
        try:
            user.save()
        except Exception as e:
            log.error(
                "Error updating user to database. {0}".format(
                    str(e)))
            return False

    def get_user_by_id(self, pk):
        return User.objects(pk=pk).first()

    def load_user(self, pk):
        return self.get_user_by_id(pk)


    """
        ----------------------------------------
            PERMISSION MANAGEMENT
        ----------------------------------------
    """
    def add_role(self, name):
        role = self.find_role(name)
        if role is None:
            try:
                role = Role(name=name)
                role.save()
                return role
            except Exception as e:
                log.error("Add Role: {0}".format(str(e)))
        return role

    def find_role(self, name):
        return Role.objects(name=name).first()

    def get_all_roles(self):
        return Role.objects

    def get_public_permissions(self):
        role = self.find_role(self.auth_role_public)
        return role.permissions

    def find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        return Permission.objects(name=name).first()

    def add_permission(self, name):
        """
            Adds a permission to the backend, model permission
            
            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm is None:
            try:
                perm = Permission(name=name)
                perm.save()
                return perm
            except Exception as e:
                log.error("Add Permission: {0}".format(str(e)))
        return perm

    def del_permission(self, name):
        """
            Deletes a permission from the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm:
            try:
                perm.delete()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))

    # ----------------------------------------------
    #       PRIMITIVES VIEW MENU
    #----------------------------------------------
    def find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        return ViewMenu.objects(name=name).first()

    def get_all_view_menu(self):
        return ViewMenu.objects

    def add_view_menu(self, name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        view_menu = self.find_view_menu(name)
        if view_menu is None:
            try:
                view_menu = ViewMenu(name=name)
                view_menu.save()
                return view_menu
            except Exception as e:
                log.error("Add View Menu Error: {0}".format(str(e)))
        return view_menu

    def del_view_menu(self, name):
        """
            Deletes a ViewMenu from the backend

            :param name:
                name of the ViewMenu
        """
        obj = self.find_view_menu(name)
        if obj:
            try:
                obj.delete()
            except Exception as e:
                log.error("Del Permission Error: {0}".format(str(e)))

    #----------------------------------------------
    #          PERMISSION VIEW MENU
    #----------------------------------------------
    def find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        permission = self.find_permission(permission_name)
        view_menu = self.find_view_menu(view_menu_name)
        return PermissionView.objects(permission=permission, view_menu=view_menu).first()

    def find_permissions_view_menu(self, view_menu):
        """
            Finds all permissions from ViewMenu, returns list of PermissionView

            :param view_menu: ViewMenu object
            :return: list of PermissionView objects
        """
        return PermissionView.objects(view_menu=view_menu)

    def add_permission_view_menu(self, permission_name, view_menu_name):
        """
            Adds a permission on a view or menu to the backend
            
            :param permission_name:
                name of the permission to add: 'can_add','can_edit' etc...
            :param view_menu_name:
                name of the view menu to add
        """
        vm = self.add_view_menu(view_menu_name)
        perm = self.add_permission(permission_name)
        pv = PermissionView()
        pv.view_menu, pv.permission = vm, perm
        try:
            pv.save()
            log.info("Created Permission View: %s" % (str(pv)))
            return pv
        except Exception as e:
            log.error("Creation of Permission View Error: {0}".format(str(e)))

    def del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            pv = self.find_permission_view_menu(permission_name, view_menu_name)
            # delete permission on view
            pv.delete()
            # if no more permission on permission view, delete permission
            pv = PermissionView.objects(permission=pv.permission)
            if not pv:
                self.del_permission(pv.permission.name)
            log.info("Removed Permission View: %s" % (str(permission_name)))
        except Exception as e:
            log.error("Remove Permission from View Error: {0}".format(str(e)))

    def exist_permission_on_views(self, lst, item):
        for i in lst:
            if i.permission.name == item:
                return True
        return False

    def exist_permission_on_view(self, lst, permission, view_menu):
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
                role.save()
                log.info("Added Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Add Permission to Role Error: {0}".format(str(e)))

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
                role.save()
                log.info("Removed Permission %s to role %s" % (str(perm_view), role.name))
            except Exception as e:
                log.error("Remove Permission to Role Error: {0}".format(str(e)))
