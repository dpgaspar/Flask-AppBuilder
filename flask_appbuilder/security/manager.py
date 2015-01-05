import datetime
import logging
from flask import url_for, g
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, current_user
from flask_openid import OpenID

from ..basemanager import BaseManager

log = logging.getLogger(__name__)

# Constants for supported authentication types
AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2
AUTH_REMOTE_USER = 3
AUTH_OAUTH = 4

ADMIN_USER_NAME = 'admin'
ADMIN_USER_PASSWORD = 'general'
ADMIN_USER_EMAIL = 'admin@fab.org'
ADMIN_USER_FIRST_NAME = 'Admin'
ADMIN_USER_LAST_NAME = 'User'


class AbstractSecurityManager(BaseManager):
    """
        Abstract SecurityManager class, declares all methods used by the
        framework. There is no assumptions about security models or auth types.
    """
    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend

            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        raise NotImplementedError

    def add_permissions_menu(self, view_menu_name):
        """
            Adds menu_access to menu on permission_view_menu

            :param view_menu_name:
                The menu name
        """
        raise NotImplementedError

    def register_views(self):
        """
            Generic function to create views
        """
        raise NotImplementedError

    def is_item_public(self, permission_name, view_name):
        """
            Check if view has public permissions

            :param permission_name:
                the permission: can_show, can_edit...
            :param view_name:
                the name of the class view (child of BaseView)
        """
        raise NotImplementedError

    def has_access(self, permission_name, view_name):
        """
            Check if current user or public has access to view or menu
        """
        raise NotImplementedError



class BaseSecurityManager(AbstractSecurityManager):

    def __init__(self, appbuilder):
        super(BaseSecurityManager, self).__init__(appbuilder)
        app = self.appbuilder.get_app
        # Base Security Config
        app.config.setdefault('AUTH_ROLE_ADMIN', 'Admin')
        app.config.setdefault('AUTH_ROLE_PUBLIC', 'Public')
        app.config.setdefault('AUTH_TYPE', AUTH_DB)
        # Self Registration
        app.config.setdefault('AUTH_USER_REGISTRATION', False)
        app.config.setdefault('AUTH_USER_REGISTRATION_ROLE', self.auth_role_public)
        # LDAP Config
        app.config.setdefault('AUTH_LDAP_SEARCH', '')
        app.config.setdefault('AUTH_LDAP_BIND_FIELD', 'cn')
        app.config.setdefault('AUTH_LDAP_UID_FIELD', 'uid')
        app.config.setdefault('AUTH_LDAP_FIRSTNAME_FIELD', 'givenName')
        app.config.setdefault('AUTH_LDAP_LASTNAME_FIELD', 'sn')
        app.config.setdefault('AUTH_LDAP_EMAIL_FIELD', 'mail')

        if self.auth_type == AUTH_LDAP:
            if 'AUTH_LDAP_SERVER' not in app.config:
                raise Exception("No AUTH_LDAP_SERVER defined on config with AUTH_LDAP authentication type.")
        if self.auth_type == AUTH_OID:
            self.oid = OpenID(app)
        if self.auth_type == AUTH_OAUTH:
            from flask_oauth import OAuth
            self.oauth = OAuth

        self.lm = LoginManager(app)
        self.lm.login_view = 'login'
        self.lm.user_loader(self.load_user)

    @property
    def get_url_for_registeruser(self):
        return url_for('%s.%s' % (self.registeruser_view.endpoint, self.registeruser_view.default_view))

    @property
    def auth_type(self):
        return self.appbuilder.get_app.config['AUTH_TYPE']

    @property
    def auth_role_admin(self):
        return self.appbuilder.get_app.config['AUTH_ROLE_ADMIN']

    @property
    def auth_role_public(self):
        return self.appbuilder.get_app.config['AUTH_ROLE_PUBLIC']

    @property
    def auth_ldap_server(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_SERVER']

    @property
    def auth_user_registration(self):
        return self.appbuilder.get_app.config['AUTH_USER_REGISTRATION']

    @property
    def auth_user_registration_role(self):
        return self.appbuilder.get_app.config['AUTH_USER_REGISTRATION_ROLE']

    @property
    def auth_ldap_search(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_SEARCH']

    @property
    def auth_ldap_bind_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_BIND_FIELD']

    @property
    def auth_ldap_uid_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_UID_FIELD']

    @property
    def auth_ldap_firstname_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_FIRSTNAME_FIELD']

    @property
    def auth_ldap_lastname_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_LASTNAME_FIELD']

    @property
    def auth_ldap_email_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_EMAIL_FIELD']

    @property
    def openid_providers(self):
        return self.appbuilder.get_app.config['OPENID_PROVIDERS']

    @property
    def oauth_providers(self):
        return self.appbuilder.get_app.config['OAUTH_PROVIDERS']

    def create_db(self):
        if self.add_role(self.auth_role_admin):
                    log.info("Inserted Role for public access %s" % (self.auth_role_admin))
        if self.add_role(self.auth_role_public):
            log.info("Inserted Role for public access %s" % (self.auth_role_public))
        if self.count_users() == 0:
            self.add_user(
                    username=ADMIN_USER_NAME,
                    first_name=ADMIN_USER_FIRST_NAME,
                    last_name=ADMIN_USER_LAST_NAME,
                    email=ADMIN_USER_EMAIL,
                    role=self.find_role(self.auth_role_admin),
                    password=generate_password_hash(ADMIN_USER_PASSWORD)
                )
            log.info("Inserted initial Admin user")
            log.info("Login using {0}/{1}".format(ADMIN_USER_NAME, ADMIN_USER_PASSWORD))

    def reset_password(self, userid, password):
        """
            Change/Reset a user's password for authdb.
            Password will be hashed and saved.

            :param userid:
                the user.id to reset the password
            :param password:
                The clear text password to reset and save hashed on the db
        """
        user = self.get_user_by_id(userid)
        user.password = generate_password_hash(password)
        self.update_user(user)

    def update_user_auth_stat(self, user, success=True):
        """
            Update authentication successful to user.

            :param user:
                The authenticated user model
        """
        if not user.login_count:
            user.login_count = 0
        if not user.fail_login_count:
            user.fail_login_count = 0
        if success:
            user.login_count += 1
            user.fail_login_count = 0
        else:
            user.fail_login_count += 1
        user.last_login = datetime.datetime.now()
        self.update_user(user)

    #---------------------------------------
    #    INTERFACE METHODS
    #---------------------------------------
    def get_user_by_id(self, pk):
        """
            Generic function to return user by it's id (pk)
        """
        raise NotImplementedError

    def add_user(self, username, first_name, last_name, email, role, password=''):
        """
            Generic function to create user
        """
        raise NotImplementedError

    def update_user(self, user):
        """
            Generic function to create user

            :param user: User model to update to database
        """
        raise NotImplementedError

    def count_users(self):
        """
            Generic function to count the existing users
        """
        raise NotImplementedError

    def auth_user_db(self, username, password):
        """
            Method for authenticating user, auth db style

            :param username:
                The username
            :param password:
                The password, will be tested against hashed password on db
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def auth_user_oid(self, email):
        """
            OpenID user Authentication

            :type self: User model
        """
        raise NotImplementedError

    def auth_user_remote_user(self, username):
        """
            REMOTE_USER user Authentication

            :type self: User model
        """
        raise NotImplementedError

    def find_role(self, name):
        raise NotImplementedError

    def add_role(self, name):
        raise NotImplementedError

    def get_public_permissions(self):
        raise NotImplementedError

    def security_cleanup(self, baseviews, menus):
        raise NotImplementedError

    def load_user(self, pk):
        return self.get_user_by_id(int(pk))

    @staticmethod
    def before_request():
        g.user = current_user
