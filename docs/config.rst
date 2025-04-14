Base Configuration
==================

Configuration keys
------------------

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap's default theme:

- SQLALCHEMY_DATABASE_URI
    - Description: DB connection string (flask-sqlalchemy)
    - Mandatory: Conditional
- SECRET_KEY
    - Description: Flask secret key used for securely signing the session cookie. Set the secret_key on the application to something unique and secret.
    - Mandatory: Yes
- MONGODB_SETTINGS
    - Description: DB connection string (flask-mongoengine)
    - Mandatory: Conditional
- AUTH_TYPE
    - Description: This is the authentication type
        - 0 = Open ID
        - 1 = Database style (user/password)
        - 2 = LDAP, use AUTH_LDAP_SERVER also
        - 3 = uses web server environment variable REMOTE_USER
        - 4 = USE ONE OR MANY OAUTH PROVIDERS
    - Mandatory: Yes
- AUTH_USER_REGISTRATION
    - Description: Set to True to enable user self-registration
    - Mandatory: No
- AUTH_USERNAME_CI
    - Description: Make auth login CI of not defaults to true
    - Mandatory: No
- AUTH_USER_REGISTRATION_ROLE
    - Description: Set role name, to be assigned when a user registers himself. This role must already exist. Mandatory when using user registration
    - Mandatory: Conditional
- AUTH_USER_REGISTRATION_ROLE_JMESPATH
    - Description: The `JMESPath <http://jmespath.org/>`_ expression used to evaluate user role on registration. If set, takes precedence over ``AUTH_USER_REGISTRATION_ROLE``. Requires ``jmespath`` to be installed. See :ref:`jmespath-examples` for examples
    - Mandatory: No
- AUTH_REMOTE_USER_ENV_VAR
    - Description: When using AUTH_TYPE = AUTH_REMOTE_USER, optionally set the wsgi environment variable that holds the current logged in user. Default: REMOTE_USER
    - Mandatory: No
- AUTH_ROLES_SYNC_AT_LOGIN
    - Description: Sets if user's roles are replaced each login with those received from LDAP/OAUTH. Default: False
    - Mandatory: No
- AUTH_ROLES_MAPPING
    - Description: A mapping from LDAP/OAUTH group names to FAB roles. See example under AUTH_LDAP_GROUP_FIELD
    - Mandatory: No
- AUTH_LDAP_SERVER
    - Description: Define your ldap server when AUTH_TYPE=2. For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new". For using LDAP over TLS, set the protocol scheme to "ldaps" and set "AUTH_LDAP_USE_TLS = False"
    - Mandatory: Conditional
- AUTH_LDAP_USE_TLS
    - Description: Require the use of STARTTLS
    - Mandatory: No
- AUTH_LDAP_BIND_USER
    - Description: Define the DN for the user that will be used for the initial LDAP BIND. This is necessary for OpenLDAP and can be used on MSFT AD. For example, AUTH_LDAP_BIND_USER = "cn=queryuser,dc=example,dc=com"
    - Mandatory: No
- AUTH_LDAP_BIND_PASSWORD
    - Description: Define password for the bind user.
    - Mandatory: No
- AUTH_LDAP_TLS_DEMAND
    - Description: Demands TLS peer certificate checking (Bool)
    - Mandatory: No
- AUTH_LDAP_TLS_CACERTDIR
    - Description: CA Certificate directory to check peer certificate. Certificate files must be PEM-encoded
    - Mandatory: No
- AUTH_LDAP_TLS_CACERTFILE
    - Description: CA Certificate file to check peer certificate. File must be PEM-encoded
    - Mandatory: No
- AUTH_LDAP_TLS_CERTFILE
    - Description: Certificate file for client auth use with AUTH_LDAP_TLS_KEYFILE
    - Mandatory: No
- AUTH_LDAP_TLS_KEYFILE
    - Description: Certificate key file for client auth
    - Mandatory: No
- AUTH_LDAP_SEARCH
    - Description: Use search with self user registration or when using AUTH_LDAP_BIND_USER. For example, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example"
    - Mandatory: No
- AUTH_LDAP_SEARCH_FILTER
    - Description: Filter or limit allowable users from the LDAP server, e.g., only the people on your team. For example, AUTH_LDAP_SEARCH_FILTER = "(memberOf=cn=group name,OU=type,dc=ex,cn=com)"
    - Mandatory: No
- AUTH_LDAP_UID_FIELD
    - Description: If doing an indirect bind to ldap, this is the field that matches the username when searching for the account to bind to. For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example", AUTH_LDAP_UID_FIELD = "uid"
    - Mandatory: No
- AUTH_LDAP_GROUP_FIELD
    - Description: Sets the field in the ldap directory that stores the user's group uids. This field is used in combination with AUTH_ROLES_MAPPING to propagate the users groups into the User database. Default is "memberOf". For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example", AUTH_LDAP_GROUP_FIELD = "memberOf", AUTH_ROLES_MAPPING = { "cn=User,ou=groups,dc=example,dc=com": ["User"] }
    - Mandatory: No
- AUTH_LDAP_FIRSTNAME_FIELD
    - Description: Sets the field in the ldap directory that stores the user's first name. This field is used to propagate user's first name into the User database. Default is "givenName". For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example", AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
    - Mandatory: No
- AUTH_LDAP_LASTNAME_FIELD
    - Description: Sets the field in the ldap directory that stores the user's last name. This field is used to propagate user's last name into the User database. Default is "sn". For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example", AUTH_LDAP_LASTNAME_FIELD = "sn"
    - Mandatory: No
- AUTH_LDAP_EMAIL_FIELD
    - Description: Sets the field in the ldap directory that stores the user's email address. This field is used to propagate user's email address into the User database. Default is "mail". For example, AUTH_TYPE = 2, AUTH_LDAP_SERVER = "ldap://ldapserver.new", AUTH_LDAP_SEARCH = "ou=people,dc=example", AUTH_LDAP_EMAIL_FIELD = "mail"
    - Mandatory: No
- AUTH_LDAP_ALLOW_SELF_SIGNED
    - Description: Allow LDAP authentication to use self-signed certificates (LDAPS)
    - Mandatory: No
- AUTH_LDAP_APPEND_DOMAIN
    - Description: Append a domain to all logins. No need to use john@domain.local. Set it like: AUTH_LDAP_APPEND_DOMAIN = 'domain.local'. And the user can login using just 'john'
    - Mandatory: No
- AUTH_LDAP_USERNAME_FORMAT
    - Description: It converts username to specific format for LDAP authentications. For example, username = "userexample", AUTH_LDAP_USERNAME_FORMAT="format-%s". It authenticates with "format-userexample".
    - Mandatory: No
- AUTH_ROLE_ADMIN
    - Description: Configure the name of the admin role.
    - Mandatory: No
- AUTH_ROLE_PUBLIC
    - Description: Special Role that holds the public permissions, no authentication needed.
    - Mandatory: No
- AUTH_API_LOGIN_ALLOW_MULTIPLE_PROVIDERS
    - Description: Allow REST API login with alternative auth providers (default False)
    - Mandatory: No
- APP_NAME
    - Description: The name of your application.
    - Mandatory: No
- APP_THEME
    - Description: Various themes for you to choose from (bootwatch).
    - Mandatory: No
- APP_ICON
    - Description: Path of your application icons will be shown on the left side of the menu
    - Mandatory: No
- ADDON_MANAGERS
    - Description: A list of addon manager's classes. Take a look at addon chapter on docs.
    - Mandatory: No
- UPLOAD_FOLDER
    - Description: Files upload folder. Mandatory for file uploads.
    - Mandatory: No
- FILE_ALLOWED_EXTENSIONS
    - Description: Tuple with allowed extensions. FILE_ALLOWED_EXTENSIONS = ('txt','doc')
    - Mandatory: No
- IMG_UPLOAD_FOLDER
    - Description: Image upload folder. Mandatory for image uploads.
    - Mandatory: No
- IMG_UPLOAD_URL
    - Description: Image relative URL. Mandatory for image uploads.
    - Mandatory: No
- IMG_SIZE
    - Description: Tuple to define default image resize. (width, height, True|False)
    - Mandatory: No
- BABEL_DEFAULT_LOCALE
    - Description: Babel's default language.
    - Mandatory: No
- LANGUAGES
    - Description: A dictionary mapping the existing languages with the countries name and flag
    - Mandatory: No
- LOGOUT_REDIRECT_URL
    - Description: The location to redirect to after logout
    - Mandatory: No
- FAB_API_SHOW_STACKTRACE
    - Description: Sends api stack trace on uncaught exceptions. (Boolean)
    - Mandatory: No
- FAB_API_MAX_PAGE_SIZE
    - Description: Sets a limit for FAB Model Api page size
    - Mandatory: No
- FAB_API_SWAGGER_UI
    - Description: Enables a Swagger UI view (Boolean)
    - Mandatory: No
- FAB_API_SWAGGER_TEMPLATE
    - Description: Path of your custom Swagger Template
    - Mandatory: No
- FAB_API_ALLOW_JSON_QS
    - Description: Allow query string parameters to be JSON. Default is True (Boolean)
    - Mandatory: No
- FAB_CREATE_DB
    - Description: Create the database if it does not exist. Default is True (Boolean)
    - Mandatory: No
- FAB_UPDATE_PERMS
    - Description: Enables or disables update permissions. Default is True (Boolean)
    - Mandatory: No
- FAB_SECURITY_MANAGER_CLASS
    - Description: Declare a new custom SecurityManager class
    - Mandatory: No
- FAB_ADD_SECURITY_API
    - Description: [Beta] Adds a CRUD REST API for users, roles, permissions, view_menus. Further details on /swagger/v1. All endpoints are under /api/v1/sercurity/. [Note]: This feature is still in beta, breaking changes are likely to occur
    - Mandatory: No
- FAB_ADD_SECURITY_VIEWS
    - Description: Enables or disables registering all security views (boolean default:True)
    - Mandatory: No
- FAB_ADD_SECURITY_PERMISSION_VIEW
    - Description: Enables or disables registering the permission view (boolean default:True)
    - Mandatory: No
- FAB_ADD_SECURITY_VIEW_MENU_VIEW
    - Description: Enables or disables registering the view_menu view (boolean default:True)
    - Mandatory: No
- FAB_ADD_SECURITY_PERMISSION_VIEWS_VIEW
    - Description: Enables or disables registering the pmv views (boolean default:True)
    - Mandatory: No
- FAB_ADD_OPENAPI_VIEWS
    - Description: Enables or disables registering all OPENAPI views (boolean default:True)
    - Mandatory: No
- FAB_OPENAPI_SERVERS
    - Description: Used for setting OpenApi Swagger UI servers if not set Swagger will use the current request host URL
    - Mandatory: No
- FAB_ROLES
    - Description: Configure builtin roles see Security chapter for further detail
    - Mandatory: No
- FAB_INDEX_VIEW
    - Description: Path of your custom IndexView class (str)
    - Mandatory: No
- FAB_MENU
    - Description: Path of your custom Menu class (str)
    - Mandatory: No
- FAB_BASE_TEMPLATE
    - Description: Path of your custom base template
    - Mandatory: No
- FAB_STATIC_FOLDER
    - Description: Path to override default static folder
    - Mandatory: No
- FAB_STATIC_URL_PATH
    - Description: Path to override default static folder
    - Mandatory: No
- FAB_PASSWORD_COMPLEXITY_VALIDATOR
    - Description: Hook for your own custom password validator function
    - Mandatory: No
- FAB_PASSWORD_COMPLEXITY_ENABLED
    - Description: Enables the password complexity validation for AUTH database users. Default is False
    - Mandatory: No

Note
----

Make sure you set your own `SECRET_KEY` to something unique and secret. This secret key is used by Flask for
securely signing the session cookie and can be used for any other security related needs by extensions or your application.
It should be a long random bytes or str. For example, copy the output of this to your config::

    $ python -c 'import secrets; print(secrets.token_hex())'
    '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

Using config.py
---------------
 
My favorite way, and the one I advise if you are building a medium to large size application
is to place all your configuration keys on a config.py file
 
Next you only have to import them to the Flask app object, like this
::

    app = Flask(__name__)
    app.config.from_object('config')

Take a look at the skeleton `config.py <https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py.tpl>`_


.. _jmespath-examples:

Using JMESPath to map user registration role
--------------------------------------------

If user self registration is enabled and ``AUTH_USER_REGISTRATION_ROLE_JMESPATH`` is set, it is 
used as a `JMESPath <http://jmespath.org/>`_ expression to evalate user registration role. The input
values is ``userinfo`` dict, returned by ``get_oauth_user_info`` function of Security Manager.
Usage of JMESPath expressions requires `jmespath <https://pypi.org/project/jmespath/>`_ package 
to be installed.

In case of Google OAuth, userinfo contains user's email that can be used to map some users as admins
and rest of the domain users as read only users. For example, this expression:
``contains(['user1@domain.com', 'user2@domain.com'], email) && 'Admin' || 'Viewer'``
causes users 1 and 2 to be registered with role ``Admin`` and rest with the role ``Viewer``.

JMESPath expression allow more groups to be evaluated:
``email == 'user1@domain.com' && 'Admin' || (email == 'user2@domain.com' && 'Op' || 'Viewer')``

For more example, see `specification <https://jmespath.org/specification.html>`_.
