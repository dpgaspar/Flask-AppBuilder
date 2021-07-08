Command Line Manager
====================

Since version 1.13.1 F.A.B. has a new command line manager, integrated with Flask cli.
The old ``fabmanager`` command line is now deprecated and will be completely removed on 2.2.X.
It's very easy to migrate to the new command line, all sub commands are still the same and
use the same parameters.

To use the new commands integrated with **Flask cli** you must specify on to import your app.
Take a look at `Flask docs <http://flask.pocoo.org/docs/cli/>`_.::

    # Using the default skeleton application
    $ export FLASK_APP=app

    # Using factory app pattern
    $ FLASK_APP="app:create_app('config')"

FAB creates a **Flask** command group named ``fab``, so all commands are issued like::

    $ flask fab <command> <parameters>

To Run your application on development::

    $ flask run --with-threads --reload

Take a quick look to the current possibilities. (The bold ones require app context)

  - babel-compile - Babel, Compiles all translations

  - babel-extract - Babel, Extracts and updates all messages.

  - **create-admin** - Creates an admin user

  - **create-user** - Create user with arbitrary role

  - create-app - Create a Skeleton application (SQLAlchemy or MongoEngine).

  - create-addon - Create a Skeleton AddOn.

  - **create-db** - Create all your database objects (SQLAlchemy only)

  - **collect-static** - Copies static files from flask-appbuilder to your static folder. Nice to have on certain deploys

  - **export-roles** - Export roles with permissions and view menus to JSON file.

  - **import-roles** - Import roles with permissions and view menus from JSON file.

  - **list-users** - List all users on the database.

  - **list-views** - List all registered views.

  - **reset-password** - Resets a user's password.

  - **security-cleanup** - Cleanup unused permissions from views and roles. :doc:`security`

  - **security-converge** - Converges all security view and permission names from all your roles. :doc:`security`

  - **upgrade-db** - Upgrade your database after F.A.B upgrade.

  - **version** - Flask-AppBuilder package version.

Command Line uses the excellent click package, so you can have a detailed help for each command, for instance::

    $ flask fab create-app --help
    Usage: flask fab create-app [OPTIONS]

    Create a Skeleton application

    Options:
    --name TEXT                     Your application name, directory will have
                                  this name
    --engine [SQLAlchemy|MongoEngine]
                                  Write your engine type
    --help                          Show this message and exit.


**create-app** - Create new Applications
----------------------------------------

To create a ready to dev skeleton application, you can use this command for SQLAlchemy engine and MongoEngine (MongoDB).
This commands needs an internet connection to **github.com**, because it will download a zip version of the skeleton repos.

**create-admin** - Create an admin user
---------------------------------------

Use this to create your first **Admin** user, or additional ones.
This admin user can be used to any type of authentication method configured, but *flask fab create-admin*
will not check it, so it will always ask for a password (assumes AUTH_DB).

**babel-extract** - Babel, Extracts and updates all messages.
-------------------------------------------------------------

Use multi **-k** options separated by space to specify how to locate the strings you want to translate. 
Default values: **lazy_gettext, gettext, _, __**.
For example::

    flask fab babel-extract --target flask_appbuilder/translations/ -k _ -k __

**create-addon** - Create new AddOns
------------------------------------

To create a ready to dev skeleton addon.
This commands needs an internet connection to **github.com**, because it will download a zip version of the skeleton repos.

**collect-static** - Collect static files
-----------------------------------------

Use this to copy all static files from flask-appbuilder package to your application static folder. Nice to have
on certain deploys, if your web server is serving the static files directly.

**upgrade-db** - Upgrade your database after F.A.B. upgrade to 1.3.0
--------------------------------------------------------------------

Will upgrade your database, necessary if you're already using F.A.B. Users now are able to have multiple roles.
Take a look at :doc:`versionmigration`

**reset-password** - Resets a user's password.
----------------------------------------------

Reset a user's password
