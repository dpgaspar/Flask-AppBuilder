Base Configuration
==================

Configuration keys
------------------

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap 3.1.1 base theme:

+-----------------------------------+--------------------------------------------+-----------+
| Key                               | Description                                | Mandatory |
+===================================+============================================+===========+
| SQLALCHEMY_DATABASE_URI           | Database connection string                 |   Yes     |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_TYPE = 0 | 1 | 2             | This is the authentication type            |   Yes     |
|                                   |  - 0 = Open ID                             |           |
|                                   |  - 1 = Database style (user/password)      |           |
|                                   |  - 2 = LDAP, use AUTH_LDAP_SERVER also     |           |
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
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_SEARCH                  | define your ldap server to do indirect     |   No      |
|                                   | bind by searching for the bind field.      |           |
|                                   | Comment out or leave blank to do direct    |           | 
|                                   | bind to ldap server.                       |           |
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_BIND_FIELD              | if doing an indirect bind to ldap, this    |   No      |
|                                   | is the field to bind to.                   |           |
|                                   | Default is "cn".                           |           | 
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   | AUTH_LDAP_BIND_FIELD = "cn"                |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_UID_FIELD               | if doing an indirect bind to ldap, this    |   No      |
|                                   | is the field that matches the username     |           |
|                                   | when searching for the account to bind     |           | 
|                                   | to.                                        |           |
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   | AUTH_LDAP_UID_FIELD = "uid"                |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_FIRSTNAME_FIELD         | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's first name. This field   |           |
|                                   | is used to propagate user's first name     |           | 
|                                   | into the User database.                    |           |
|                                   | Default is "givenName".                    |           | 
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   | AUTH_LDAP_FIRSTNAME_FIELD = "givenName"    |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_LASTNAME_FIELD          | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's last name. This field    |           |
|                                   | is used to propagate user's last name      |           | 
|                                   | into the User database.                    |           |
|                                   | Default is "sn".                           |           | 
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   | AUTH_LDAP_LASTNAME_FIELD = "sn"            |           |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_LDAP_EMAIL_FIELD             | sets the field in the ldap directory that  |   No      |
|                                   | stores the user's email address. This      |           |
|                                   | field is used to propagate user's email    |           | 
|                                   | address into the User database.            |           |
|                                   | Default is "mail".                         |           | 
|                                   | example:                                   |           |
|                                   | AUTH_TYPE = 2                              |           |
|                                   | AUTH_LDAP_SERVER = "ldap://ldapserver.new" |           |
|                                   | AUTH_LDAP_SEARCH = "ou=people,dc=example"  |           |
|                                   | AUTH_LDAP_EMAIL_FIELD = "mail"             |           |
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
| IMG_UPLOAD_FOLDER                 | Image upload folder.                       |   No      |
|                                   | Mandatory for image uploads.               |           |
+-----------------------------------+--------------------------------------------+-----------+
| IMG_UPLOAD_URL                    | Image relative URL.                        |   No      |
|                                   | Mandatory for image uploads.               |           |
+-----------------------------------+--------------------------------------------+-----------+
| IMG_SIZE                          | tuple to define image resize.              |   No      |
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
