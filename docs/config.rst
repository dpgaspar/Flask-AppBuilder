Base Configuration
==================

Configuration keys
------------------

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap's default theme:

    .. cssclass:: table-bordered table-hover

+-----------------------------------+--------------------------------------------+-----------+
| Key                               | Description                                | Mandatory |
+===================================+============================================+===========+
| SQLALCHEMY_DATABASE_URI           | DB connection string (flask-sqlalchemy)    |   Cond.   |
+-----------------------------------+--------------------------------------------+-----------+
| MONGODB_SETTINGS                  | DB connection string (flask-mongoengine)   |   Cond.   |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_TYPE = 0 | 1 | 2 | 3 | 4     | This is the authentication type            |   Yes     |
|           or                      |  - 0 = Open ID                             |           |
| AUTH_TYPE = AUTH_OID, AUTH_DB,    |  - 1 = Database style (user/password)      |           |
|            AUTH_LDAP, AUTH_REMOTE |  - 2 = LDAP, use AUTH_LDAP_SERVER also     |           |
|            AUTH_OAUTH             |  - 3 = uses web server environ var         |           |
|                                   |        REMOTE_USER                         |           |
|                                   |  - 4 = USE ONE OR MANY OAUTH PROVIDERS     |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_USER_REGISTRATION =          | Set to True to enable user self            |   No      |
| True|False                        | registration                               |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_USER_REGISTRATION_ROLE       | Set role name, to be assign when a user    |   Cond.   |
|                                   | registers himself. This role must already  |           |
|                                   | exist. Mandatory when using user           |           |
|                                   | registration                               |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_SERVER                  | define your ldap server when AUTH_TYPE=2   |   Cond.   |
|                                   | example:                                   |           |
|                                   |                                            |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_BIND_USER               | Define the DN for the user that will be    |   No      |
|                                   | used for the initial LDAP BIND.            |           |
|                                   | This is necessary for OpenLDAP and can be  |           |
|                                   | used on MSFT AD.                           |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_BIND_USER =                      |           |
|                                   | "cn=queryuser,dc=example,dc=com"           |           |
|                                   |                                            |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_BIND_PASSWORD           | Define password for the bind user.         |   No      |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_SEARCH                  | Use search with self user                  |   No      |
|                                   | registration or when using                 |           |
|                                   | AUTH_LDAP_BIND_USER.                       |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_UID_FIELD               | if doing an indirect bind to ldap, this    |   No      |
|                                   | is the field that matches the username     |           |
|                                   | when searching for the account to bind     |           | 
|                                   | to.                                        |           |
|                                   | example:                                   |           |
|                                   |                                            |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_UID_FIELD = "uid"                |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_FIRSTNAME_FIELD         | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's first name. This field   |           |
|                                   | is used to propagate user's first name     |           | 
|                                   | into the User database.                    |           |
|                                   | Default is "givenName".                    |           | 
|                                   | example:                                   |           |
|                                   |                                            |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_FIRSTNAME_FIELD = "givenName"    |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_LASTNAME_FIELD          | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's last name. This field    |           |
|                                   | is used to propagate user's last name      |           | 
|                                   | into the User database.                    |           |
|                                   | Default is "sn".                           |           | 
|                                   | example:                                   |           |
|                                   |                                            |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_LASTNAME_FIELD = "sn"            |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_EMAIL_FIELD             | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's email address. This      |           |
|                                   | field is used to propagate user's email    |           | 
|                                   | address into the User database.            |           |
|                                   | Default is "mail".                         |           | 
|                                   | example:                                   |           |
|                                   |                                            |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   |                                            |           |
|                                   | AUTH_LDAP_EMAIL_FIELD = "mail"             |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_ALLOW_SELF_SIGNED       | Allow LDAP authentication to use self      |   No      |
|                                   | signed certificates                        |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_ROLE_ADMIN                   | Configure the name of the admin role.      |   No      |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_ROLE_PUBLIC                  | Special Role that holds the public         |   No      |
|                                   | permissions, no authentication needed.     |           |
+-----------------------------------+--------------------------------------------+-----------+
| APP_NAME                          | The name of your application.              |   No      |
+-----------------------------------+--------------------------------------------+-----------+
| APP_THEME                         | Various themes for you to choose           |   No      |
|                                   | from (bootwatch).                          |           |
+-----------------------------------+--------------------------------------------+-----------+
| APP_ICON                          | path of your application icons             |   No      |
|                                   | will be shown on the left side of the menu |           |
+-----------------------------------+--------------------------------------------+-----------+
| UPLOAD_FOLDER                     | Files upload folder.                       |   No      |
|                                   | Mandatory for file uploads.                |           |
+-----------------------------------+--------------------------------------------+-----------+
| FILE_ALLOWED_EXTENSIONS           | Tuple with allower extensions.             |   No      |
|                                   | FILE_ALLOWED_EXTENSIONS = ('txt','doc')    |           |
+-----------------------------------+--------------------------------------------+-----------+
| IMG_UPLOAD_FOLDER                 | Image upload folder.                       |   No      |
|                                   | Mandatory for image uploads.               |           |
+-----------------------------------+--------------------------------------------+-----------+
| IMG_UPLOAD_URL                    | Image relative URL.                        |   No      |
|                                   | Mandatory for image uploads.               |           |
+-----------------------------------+--------------------------------------------+-----------+
| IMG_SIZE                          | tuple to define default image resize.      |   No      |
|                                   | (width, height, True|False).               |           |
+-----------------------------------+--------------------------------------------+-----------+
| BABEL_DEFAULT_LOCALE              | Babel's default language.                  |   No      |
+-----------------------------------+--------------------------------------------+-----------+
| LANGUAGES                         | A dictionary mapping                       |   No      |
|                                   | the existing languages with the countries  |           |
|                                   | name and flag                              |           |
+-----------------------------------+--------------------------------------------+-----------+


Using config.py
---------------
 
My favorite way, and the one i advise if you are building a medium to large size application
is to place all your configuration keys on a config.py file
 
next you only have to import them to the Flask app object, like this
::

    app = Flask(__name__)
    app.config.from_object('config')

Take a look at the skeleton `config.py <https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py>`_
