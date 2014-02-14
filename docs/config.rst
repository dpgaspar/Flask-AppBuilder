Base Configuration
==================

Configuration keys
------------------

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

+-----------------------------------+--------------------------------------------+-----------+
| Key                               | Description                                | Mandatory |
+===================================+============================================+===========+
| SQLALCHEMY_DATABASE_URI           | Database connection string                 |   Yes     |
+-----------------------------------+--------------------------------------------+-----------+
| AUTH_TYPE = 0 | 1                 | This is the authentication type            |   Yes     |
|                                   |  - 0 = Open ID                             |           |
|                                   |  - 1 = Database style (user/password)      |           |
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
 
 My favorite way, and the one i advise if you are building a medium to large size application is to place all you configuration key on a config.py file
 
 next you only have to import them to the Flask app object, like this::
 
 	app = Flask(__name__)
 	app.config.from_object('config')
 
 Take a look at the skeleton `config.py <https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py>`_
