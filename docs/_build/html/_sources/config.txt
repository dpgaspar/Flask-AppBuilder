Base Configuration
==================

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

    :SQLALCHEMY_DATABASE_URI: Database connection string
    :AUTH_TYPE: This is the authentication type
        - 0 = Open ID
        - 1 = Database style (user/password)
    :AUTH_ROLE_ADMIN: Configure the name of the admin role. 
    :AUTH_ROLE_PUBLIC: Special Role that holds the public permissions, no authentication needed.
    :APP_NAME: The name of your application.
    :APP_THEME: Various themes for you to choose from (bootwatch).
    :UPLOAD_FOLDER: Files upload folder.
    :IMG_UPLOAD_FOLDER: Image upload folder.
    :IMG_UPLOAD_URL: Image relative URL.
    :BABEL_DEFAULT_LOCALE: Babel's default language.
    :LANGUAGES: A dictionary mapping the existing languages with the countrys name and flag
 
 Take a look at the skeleton :config.py:`https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py`
 


