import logging
from werkzeug.security import generate_password_hash
from ...models.mongoengine.interface import MongoEngineInterface
from .models import User, Role, PermissionView, Permission, ViewMenu
from ..views import AuthDBView, AuthOIDView, ResetMyPasswordView, AuthLDAPView, AuthOAuthView, AuthRemoteUserView, \
    ResetPasswordView, UserDBModelView, UserLDAPModelView, UserOIDModelView, UserOAuthModelView, UserRemoteUserModelView,\
    RoleModelView, PermissionViewModelView, ViewMenuModelView, PermissionModelView, UserStatsChartView
#from .registerviews import RegisterUserDBView, RegisterUserOIDView
from ..manager import BaseSecurityManager
from ... import const as c

log = logging.getLogger(__name__)


class SecurityManager(BaseSecurityManager):
    """
        Responsible for authentication, registering security views,
        role and permission auto management

        If you want to change anything just inherit and override, then
        pass your own security manager to AppBuilder.
    """
    user_model = User
    """ Override to set your own User Model """
    role_model = Role
    """ Override to set your own User Model """
    permission_model = Permission
    viewmenu_model = ViewMenu
    permissionview_model = PermissionView

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
        self.userdbmodelview.datamodel = MongoEngineInterface(self.user_model)
        self.userldapmodelview.datamodel = MongoEngineInterface(self.user_model)
        self.useroidmodelview.datamodel = MongoEngineInterface(self.user_model)
        self.useroauthmodelview.datamodel = MongoEngineInterface(self.user_model)
        self.userremoteusermodelview.datamodel = MongoEngineInterface(self.user_model)
        self.userstatschartview.datamodel = MongoEngineInterface(self.user_model)
        self.rolemodelview.datamodel = MongoEngineInterface(self.role_model)
        self.permissionmodelview.datamodel=MongoEngineInterface(self.permission_model)
        self.viewmenumodelview.datamodel=MongoEngineInterface(self.viewmenu_model)
        self.permissionviewmodelview.datamodel=MongoEngineInterface(self.permissionview_model)
        super(SecurityManager, self).__init__(appbuilder)
        self.create_db()

    def find_user(self, username=None, email=None):
        if username:
            return self.user_model.objects(username=username).first()
        elif email:
            return self.user_model.objects(email=email).first()

    def get_all_users(self):
        return User.objects

    def add_user(self, username, first_name, last_name, email, role, password=''):
        """
            Generic function to create user
        """
        try:
            user = self.user_model()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            user.roles.append(role)
            user.password = generate_password_hash(password)
            user.save()
            log.info(c.LOGMSG_INF_SEC_ADD_USER.format(username))
            return user
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_USER.format(str(e)))
            return False

    def count_users(self):
        return len(self.user_model.objects)

    def update_user(self, user):
        try:
            user.save()
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_UPD_USER.format(str(e)))
            return False

    def get_user_by_id(self, pk):
        return self.user_model.objects(pk=pk).first()

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
                role = self.role_model(name=name)
                role.save()
                log.info(c.LOGMSG_INF_SEC_ADD_ROLE.format(name))
                return role
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_ROLE.format(str(e)))
        return role

    def find_role(self, name):
        return self.role_model.objects(name=name).first()

    def get_all_roles(self):
        return self.role_model.objects

    def get_public_permissions(self):
        role = self.find_role(self.auth_role_public)
        return role.permissions

    def find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        return self.permission_model.objects(name=name).first()

    def add_permission(self, name):
        """
            Adds a permission to the backend, model permission
            
            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm is None:
            try:
                perm = self.permission_model(name=name)
                perm.save()
                return perm
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMISSION.format(str(e)))
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
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION.format(str(e)))

    # ----------------------------------------------
    #       PRIMITIVES VIEW MENU
    #----------------------------------------------
    def find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        return self.viewmenu_model.objects(name=name).first()

    def get_all_view_menu(self):
        return self.viewmenu_model.objects

    def add_view_menu(self, name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        view_menu = self.find_view_menu(name)
        if view_menu is None:
            try:
                view_menu = self.viewmenu_model(name=name)
                view_menu.save()
                return view_menu
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_VIEWMENU.format(str(e)))
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
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION.format(str(e)))

    #----------------------------------------------
    #          PERMISSION VIEW MENU
    #----------------------------------------------
    def find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        permission = self.find_permission(permission_name)
        view_menu = self.find_view_menu(view_menu_name)
        return self.permissionview_model.objects(permission=permission, view_menu=view_menu).first()

    def find_permissions_view_menu(self, view_menu):
        """
            Finds all permissions from ViewMenu, returns list of PermissionView

            :param view_menu: ViewMenu object
            :return: list of PermissionView objects
        """
        return self.permissionview_model.objects(view_menu=view_menu)

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
        pv = self.permissionview_model()
        pv.view_menu, pv.permission = vm, perm
        try:
            pv.save()
            log.info(c.LOGMSG_INF_SEC_ADD_PERMVIEW.format(str(pv)))
            return pv
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_PERMVIEW.format(str(e)))

    def del_permission_view_menu(self, permission_name, view_menu_name):
        try:
            pv = self.find_permission_view_menu(permission_name, view_menu_name)
            # delete permission on view
            pv.delete()
            # if no more permission on permission view, delete permission
            pv = self.permissionview_model.objects(permission=pv.permission)
            if not pv:
                self.del_permission(pv.permission.name)
            log.info(c.LOGMSG_INF_SEC_DEL_PERMVIEW.format(permission_name, view_menu_name))
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_PERMVIEW.format(str(e)))

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
                log.info(c.LOGMSG_INF_SEC_ADD_PERMROLE.format(str(perm_view), role.name))
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMROLE.format(str(e)))

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
                log.info(c.LOGMSG_INF_SEC_DEL_PERMROLE.format(str(perm_view), role.name))
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMROLE.format(str(e)))
