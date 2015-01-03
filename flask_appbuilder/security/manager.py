import logging

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


class BaseSecurityManager(BaseManager):
    pass


