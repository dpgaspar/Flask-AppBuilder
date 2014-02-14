Base Configuration
==================

Configuration keys
------------------

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

    :SQLALCHEMY_DATABASE_URI: Database connection string
    :AUTH_TYPE: This is the authentication type
        - 0 = Open ID
        - 1 = Database style (user/password)
    :AUTH_ROLE_ADMIN: Configure the name of the admin role. 
    :AUTH_ROLE_PUBLIC: Special Role that holds the public permissions, no authentication needed.
    :APP_NAME: The name of your application.
    :APP_THEME: Various themes for you to choose from (bootwatch).
    :APP_ICON: path of your application icon, will be shown on the left side of the menu
    :UPLOAD_FOLDER: Files upload folder. Mandatory for file uploads.
    :IMG_UPLOAD_FOLDER: Image upload folder. Mandatory for image uploads.
    :IMG_UPLOAD_URL: Image relative URL. Mandatory for image uploads.
    :IMG_SIZE: tuple to define image resize, (width, height, True|False).
    :BABEL_DEFAULT_LOCALE: Babel's default language.
    :LANGUAGES: A dictionary mapping the existing languages with the countries name and flag


Using config.py
---------------
 
 My favorite way, and the one i advise if you are building a medium to large size application is to place all you configuration key on a config.py file
 
 next you only have to import them to the Flask app object, like this::
 
 	app = Flask(__name__)
 	app.config.from_object('config')
 
 Take a look at the skeleton `config.py <https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py>`_
