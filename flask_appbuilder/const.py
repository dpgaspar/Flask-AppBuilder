from flask_babel import lazy_gettext

"""
    All constants and messages definitions go here

    Log messages obey the following rule:

        LOGMSG_<SEV>_<MODULE>_<NAME>
            <SEV> :- INF | DEB | WAR | ERR
            <MODULE> :- SEC

    Flash messages obey the following rule:

        FLAMSG_<SEV>_<MODULE>_<NAME>
            <SEV> :- INF | DEB | WAR | ERR
            <MODULE> :- SEC

"""

LOGMSG_ERR_SEC_ACCESS_DENIED = "Access is Denied for: %s on: %s"
""" Access denied log message, format with user and view/resource """
LOGMSG_WAR_SEC_LOGIN_FAILED = "Login Failed for user: %s"
LOGMSG_ERR_SEC_CREATE_DB = "DB Creation and initialization failed: %s"
""" security models creation fails, format with error message """
LOGMSG_ERR_SEC_ADD_ROLE = "Add Role: %s"
""" Error adding role, format with err message """
LOGMSG_ERR_SEC_ADD_PERMISSION = "Add Permission: %s"
""" Error adding permission, format with err message """
LOGMSG_ERR_SEC_ADD_VIEWMENU = "Add View Menu Error: %s"
""" Error adding view menu, format with err message """
LOGMSG_ERR_SEC_DEL_PERMISSION = "Del Permission Error: %s"
""" Error deleting permission, format with err message """
LOGMSG_ERR_SEC_ADD_PERMVIEW = "Creation of Permission View Error: %s"
""" Error adding permission view, format with err message """
LOGMSG_ERR_SEC_DEL_PERMVIEW = "Remove Permission from View Error: %s"
""" Error deleting permission view, format with err message """
LOGMSG_WAR_SEC_DEL_PERMVIEW = (
    "Refused to delete permission view, assoc with role exists %s.%s %s"
)
LOGMSG_WAR_SEC_DEL_PERMISSION = "Refused to delete, permission %s does not exist"
LOGMSG_WAR_SEC_DEL_VIEWMENU = "Refused to delete, view menu %s does not exist"
LOGMSG_WAR_SEC_DEL_PERM_PVM = "Refused to delete permission %s, PVM exists %s"
LOGMSG_WAR_SEC_DEL_VIEWMENU_PVM = "Refused to delete view menu %s, PVM exists %s"
LOGMSG_ERR_SEC_ADD_PERMROLE = "Add Permission to Role Error: %s"
""" Error adding permission to role, format with err message """
LOGMSG_ERR_SEC_DEL_PERMROLE = "Remove Permission to Role Error: %s"
""" Error deleting permission to role, format with err message """
LOGMSG_ERR_SEC_ADD_REGISTER_USER = "Add Register User Error: %s"
""" Error adding registered user, format with err message """
LOGMSG_ERR_SEC_DEL_REGISTER_USER = "Remove Register User Error: %s"
""" Error deleting registered user, format with err message """
LOGMSG_ERR_SEC_NO_REGISTER_HASH = "Attempt to activate user with false hash: %s"
""" Attempt to activate user with not registered hash, format with hash """
LOGMSG_ERR_SEC_AUTH_LDAP = "LDAP Error %s"
""" Generic LDAP error, format with err message """
LOGMSG_ERR_SEC_AUTH_LDAP_TLS = (
    "LDAP Could not activate TLS on established connection with %s"
)
""" LDAP Could not activate TLS on established connection with server """
LOGMSG_ERR_SEC_ADD_USER = "Error adding new user to database. %s"
""" Error adding user, format with err message """
LOGMSG_ERR_SEC_UPD_USER = "Error updating user to database. %s "
""" Error updating user, format with err message """
LOGMSG_WAR_SEC_NO_USER = "No user yet created, use flask fab command to do it."
""" Warning when app starts if no user exists on db """
LOGMSG_WAR_SEC_NOLDAP_OBJ = "No LDAP object found for: %s"

LOGMSG_INF_SEC_ADD_PERMVIEW = "Created Permission View: %s"
""" Info when adding permission view, format with permission view class string """
LOGMSG_INF_SEC_DEL_PERMVIEW = "Removed Permission View: %s on %s"
""" Info when deleting permission view, format with permission name and view name """
LOGMSG_INF_SEC_ADD_PERMROLE = "Added Permission %s to role %s"
""" Info when adding permission to role,
format with permission view class string and role name """
LOGMSG_INF_SEC_DEL_PERMROLE = "Removed Permission %s to role %s"
""" Info when deleting permission to role,
format with permission view class string and role name """
LOGMSG_INF_SEC_ADD_ROLE = "Inserted Role: %s"
""" Info when added role, format with role name """
LOGMSG_INF_SEC_NO_DB = "Security DB not found Creating all Models from Base"
LOGMSG_INF_SEC_ADD_DB = "Security DB Created"
LOGMSG_INF_SEC_ADD_USER = "Added user %s"
""" User added, format with username """
LOGMSG_INF_SEC_UPD_USER = "Updated user %s"
""" User updated, format with username """
LOGMSG_INF_SEC_UPD_ROLE = "Updated role %s"
""" Role updated, format with role name """
LOGMSG_ERR_SEC_UPD_ROLE = "An error occurred updating role %s"
""" Role updated Error, format with role name """

LOGMSG_INF_FAB_ADDON_ADDED = "Registered AddOn: %s"
""" Addon imported and registered """
LOGMSG_ERR_FAB_ADDON_IMPORT = "An error occurred when importing declared addon %s: %s"
""" Error on addon import, format with addon class path and error message """
LOGMSG_ERR_FAB_ADDON_PROCESS = "An error occurred when processing declared addon %s: %s"
""" Error on addon processing (pre, register, post),
format with addon class path and error message """


LOGMSG_ERR_FAB_ADD_PERMISSION_MENU = "Add Permission on Menu Error: %s"
""" Error when adding a permission to a menu, format with err """
LOGMSG_ERR_FAB_ADD_PERMISSION_VIEW = "Add Permission on View Error: %s"
""" Error when adding a permission to a menu, format with err """

LOGMSG_ERR_DBI_ADD_GENERIC = "Add record error: %s"
""" Database add generic error, format with err message """
LOGMSG_ERR_DBI_EDIT_GENERIC = "Edit record error: %s"
""" Database edit generic error, format with err message """
LOGMSG_ERR_DBI_DEL_GENERIC = "Delete record error: %s"
""" Database delete generic error, format with err message """
LOGMSG_WAR_DBI_AVG_ZERODIV = "Zero division on aggregate_avg"

LOGMSG_WAR_FAB_VIEW_EXISTS = "View already exists %s ignoring"
""" Attempt to add an already added view, format with view name """
LOGMSG_WAR_DBI_ADD_INTEGRITY = "Add record integrity error: %s"
""" Dabase integrity error, format with err message """
LOGMSG_WAR_DBI_EDIT_INTEGRITY = "Edit record integrity error: %s"
""" Dabase integrity error, format with err message """
LOGMSG_WAR_DBI_DEL_INTEGRITY = "Delete record integrity error: %s"
""" Dabase integrity error, format with err message """

LOGMSG_INF_FAB_ADD_VIEW = "Registering class %s on menu %s"
""" Inform that view class was added, format with class name, name"""


FLAMSG_ERR_SEC_ACCESS_DENIED = lazy_gettext("Access is Denied")
""" Access denied flash message """


PERMISSION_PREFIX = "can_"
""" Prefix to be concatenated to permission names, and inserted in the backend """

AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2
AUTH_REMOTE_USER = 3
AUTH_OAUTH = 4
""" Constants for supported authentication types """

# -----------------------------------
#  REST API Constants
# -----------------------------------

API_SECURITY_VERSION = "v1"
API_SECURITY_PROVIDER_DB = "db"
API_SECURITY_PROVIDER_LDAP = "ldap"
API_SECURITY_USERNAME_KEY = "username"
API_SECURITY_PASSWORD_KEY = "password"
API_SECURITY_PROVIDER_KEY = "provider"
API_SECURITY_REFRESH_KEY = "refresh"
API_SECURITY_ACCESS_TOKEN_KEY = "access_token"
API_SECURITY_REFRESH_TOKEN_KEY = "refresh_token"
# Response keys

API_ORDER_COLUMNS_RES_KEY = "order_columns"
API_LABEL_COLUMNS_RES_KEY = "label_columns"
API_LIST_COLUMNS_RES_KEY = "list_columns"
API_SHOW_COLUMNS_RES_KEY = "show_columns"
API_ADD_COLUMNS_RES_KEY = "add_columns"
API_EDIT_COLUMNS_RES_KEY = "edit_columns"
API_DESCRIPTION_COLUMNS_RES_KEY = "description_columns"
API_RESULT_RES_KEY = "result"
API_FILTERS_RES_KEY = "filters"
API_PERMISSIONS_RES_KEY = "permissions"

API_LIST_TITLE_RES_KEY = "list_title"
API_ADD_TITLE_RES_KEY = "add_title"
API_EDIT_TITLE_RES_KEY = "edit_title"
API_SHOW_TITLE_RES_KEY = "show_title"

# Request Rison keys

API_URI_RIS_KEY = "q"
API_ORDER_COLUMNS_RIS_KEY = "order_columns"
API_LABEL_COLUMNS_RIS_KEY = "label_columns"
API_LIST_COLUMNS_RIS_KEY = "list_columns"
API_SHOW_COLUMNS_RIS_KEY = "show_columns"
API_ADD_COLUMNS_RIS_KEY = "add_columns"
API_EDIT_COLUMNS_RIS_KEY = "edit_columns"
API_DESCRIPTION_COLUMNS_RIS_KEY = "description_columns"
API_FILTERS_RIS_KEY = "filters"
API_PERMISSIONS_RIS_KEY = "permissions"
API_SELECT_COLUMNS_RIS_KEY = "columns"
API_SELECT_KEYS_RIS_KEY = "keys"
API_ORDER_COLUMN_RIS_KEY = "order_column"
API_ORDER_DIRECTION_RIS_KEY = "order_direction"
API_PAGE_INDEX_RIS_KEY = "page"
API_PAGE_SIZE_RIS_KEY = "page_size"

API_LIST_TITLE_RIS_KEY = "list_title"
API_ADD_TITLE_RIS_KEY = "add_title"
API_EDIT_TITLE_RIS_KEY = "edit_title"
API_SHOW_TITLE_RIS_KEY = "show_title"
