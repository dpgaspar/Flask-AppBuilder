Version Migration
=================

Migrating to 5.0.0
------------------

Flask-AppBuilder 5.0.0 introduces major breaking changes to modernize the framework and improve maintainability. This version removes deprecated features and updates dependencies for better compatibility with modern Flask ecosystem.

**Major Changes Summary:**

1. **Removed MongoDB/MongoEngine Support** - Complete removal of deprecated MongoDB backend
2. **Removed OpenID 2.0 Support** - Deprecated authentication method removed (OAuth 2.0 preserved)
3. **Removed RestCRUDView** - Deprecated view class removed to simplify inheritance
4. **Updated SQLAlchemy Support** - Added SQLAlchemy 2.x and Flask-SQLAlchemy 3.x compatibility
5. **CLI Command Changes** - Updated command-line interface

Breaking Changes and Migration Guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. MongoDB/MongoEngine Removal**

MongoDB support has been completely removed. If you are using MongoDB:

**Before (v4.x):**
::

    from flask_appbuilder.security.mongoengine import MongoEngineSecurityManager
    from flask_appbuilder.models.mongoengine import ModelItem
    
    # In config.py
    SQLALCHEMY_DATABASE_URI = 'mongodb://localhost:27017/mydb'
    
    # Security manager
    appbuilder = AppBuilder(app, db.session, security_manager_class=MongoEngineSecurityManager)

**After (v5.x):**
::

    from flask_appbuilder.security.sqla import SecurityManager
    from flask_appbuilder.models.sqla import Model
    
    # In config.py  
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/mydb'  # Use SQL database
    
    # Security manager (default)
    appbuilder = AppBuilder(app, db.session)

**Migration Steps:**
1. Export your MongoDB data to SQL format
2. Set up PostgreSQL, MySQL, or SQLite database
3. Convert MongoEngine models to SQLAlchemy models
4. Update imports to use SQLAlchemy interfaces
5. Remove MongoDB dependencies from requirements.txt

**2. OpenID 2.0 Authentication Removal**

OpenID 2.0 support has been removed. Migrate to OAuth 2.0, LDAP, or database authentication.

**Before (v4.x):**
::

    # In config.py
    AUTH_TYPE = AUTH_OID
    OPENID_PROVIDERS = [
        {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
        {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    ]

**After (v5.x):**
::

    # In config.py - Use OAuth 2.0 instead
    AUTH_TYPE = AUTH_OAUTH
    OAUTH_PROVIDERS = [
        {
            'name': 'google',
            'token_key': 'access_token',
            'icon': 'fa-google',
            'remote_app': {
                'client_id': 'GOOGLE_CLIENT_ID',
                'client_secret': 'GOOGLE_CLIENT_SECRET',
                'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
                'client_kwargs': {'scope': 'email profile'},
                'server_metadata_url': 'https://accounts.google.com/.well-known/openid_configuration'
            }
        }
    ]

**Migration Steps:**
1. Remove ``AUTH_OID`` and ``OPENID_PROVIDERS`` from config
2. Set up OAuth 2.0 providers with proper client credentials
3. Update authentication type to ``AUTH_OAUTH``, ``AUTH_LDAP``, or ``AUTH_DB``
4. Test authentication flow with new providers

**3. RestCRUDView Removal**

The deprecated ``RestCRUDView`` class has been removed to simplify inheritance hierarchy.

**Before (v4.x):**
::

    from flask_appbuilder import RestCRUDView
    
    class MyView(RestCRUDView):
        datamodel = SQLAInterface(MyModel, db.session)

**After (v5.x):**
::

    from flask_appbuilder import ModelView
    
    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel, db.session)

**Migration Steps:**
1. Replace ``RestCRUDView`` imports with ``ModelView``
2. Update class inheritance from ``RestCRUDView`` to ``ModelView``
3. Remove any usage of deprecated REST API methods

**4. SQLAlchemy 2.x and Flask-SQLAlchemy 3.x Compatibility**

Flask-AppBuilder now supports both SQLAlchemy 1.4+ and 2.x with Flask-SQLAlchemy 2.x and 3.x.

**Key Changes:**

- **Query Syntax Updates**: Some query patterns may need updates for SQLAlchemy 2.x
- **Session Handling**: Improved session management compatibility
- **Relationship Loading**: Updated lazy loading syntax support

**Before (SQLAlchemy 1.x patterns):**
::

    # Old query patterns that may need updates
    users = session.query(User).filter_by(active=True).all()
    result = session.execute("SELECT * FROM users WHERE active = 1")

**After (SQLAlchemy 2.x compatible):**
::

    # Modern patterns (works with both 1.4+ and 2.x)
    from sqlalchemy import select, text
    
    users = session.scalars(select(User).where(User.active == True)).all()
    result = session.execute(text("SELECT * FROM users WHERE active = :active"), {"active": 1})

**Migration Steps:**
1. Update SQLAlchemy to 1.4+ or 2.x in your requirements
2. Update Flask-SQLAlchemy to 2.x or 3.x
3. Test your application thoroughly
4. Update any custom query patterns if needed

**5. CLI Command Changes**

The ``fab create-app`` command has been simplified.

**Before (v4.x):**
::

    fab create-app myapp --engine SQLAlchemy

**After (v5.x):**
::

    fab create-app myapp

**Migration Steps:**
1. Remove ``--engine`` parameter from scripts using ``fab create-app``
2. SQLAlchemy is now the only supported database engine

**6. Import Path Changes**

Some imports have been removed or changed:

**Removed Imports:**
::

    # These imports will fail in v5.x
    from flask_appbuilder.const import AUTH_OID  # Removed
    from flask_appbuilder.security.mongoengine import MongoEngineSecurityManager  # Removed
    from flask_appbuilder.models.mongoengine import ModelItem  # Removed
    from flask_appbuilder import RestCRUDView  # Removed

**Updated Imports:**
::

    # Use these instead
    from flask_appbuilder.const import AUTH_OAUTH, AUTH_DB, AUTH_LDAP
    from flask_appbuilder.security.sqla import SecurityManager
    from flask_appbuilder.models.sqla import Model
    from flask_appbuilder import ModelView

**7. Security Manager Session Access Changes**

The method to access the security manager's database session has changed.

**Before (v4.x):**
::

    # Old session access method
    session = appbuilder.sm.get_session

**After (v5.x):**
::

    # New session access method
    session = appbuilder.sm.session

**Migration Steps:**
1. Replace ``appbuilder.sm.get_session`` with ``appbuilder.sm.session``
2. Update any code that accesses the security manager's database session

**8. Application Context Required for Database Queries**

Database queries through the security manager now require an application context.

**Before (v4.x):**
::

    # Worked outside application context
    users = appbuilder.sm.get_all_users()

**After (v5.x):**
::

    # Requires application context
    with app.app_context():
        users = appbuilder.sm.get_all_users()

**Migration Steps:**
1. Wrap database queries in ``with app.app_context():`` blocks
2. Ensure application context is available when accessing database through security manager
3. Test all database operations in your application

**9. SQLAInterface Exception Handling Changes**

The ``SQLAInterface`` class no longer automatically swallows exceptions and includes a new ``commit`` parameter.

**Before (v4.x):**
::

    # Exceptions were automatically handled
    interface = SQLAInterface(MyModel)
    interface.add(item)  # Automatic commit

**After (v5.x):**
::

    # Exceptions are now propagated, commit parameter available
    interface = SQLAInterface(MyModel)
    interface.add(item)  # Default: commit=True
    
    # Or with manual commit control
    interface.add(item, commit=False)
    # Must call commit manually later

**Migration Steps:**
1. Add proper exception handling around ``SQLAInterface`` operations
2. Use ``commit=False`` parameter if you need manual transaction control
3. Test error handling in your data access code

**10. Application Reference Changes**

The ``appbuilder.get_app`` method has been removed.

**Before (v4.x):**
::

    # Removed method
    app = appbuilder.get_app

**After (v5.x):**
::

    # Use Flask's current_app (recommended)
    from flask import current_app
    app = current_app
    
    # Or use direct reference (deprecated)
    app = appbuilder.app

**Migration Steps:**
1. Replace ``appbuilder.get_app`` calls with ``from flask import current_app``
2. Use ``current_app`` instead of the removed method
3. Update imports to include ``current_app`` where needed

**11. Model __tablename__ Requirement**

All user models now require an explicit ``__tablename__`` attribute.

**Before (v4.x):**
::

    # tablename was optional/auto-generated
    class MyModel(Model):
        id = Column(Integer, primary_key=True)

**After (v5.x):**
::

    # tablename is now required
    class MyModel(Model):
        __tablename__ = 'my_model'
        id = Column(Integer, primary_key=True)

**Migration Steps:**
1. Add ``__tablename__`` attribute to all model classes
2. Choose appropriate table names following your naming convention
3. Ensure table names don't conflict with existing database tables

**12. New Configuration Option: FAB_CREATE_DB**

A new configuration option ``FAB_CREATE_DB`` controls automatic database table creation.

**New in v5.x:**
::

    # In config.py
    FAB_CREATE_DB = True   # Default: automatically create tables
    FAB_CREATE_DB = False  # Disable automatic table creation

**Migration Steps:**
1. Set ``FAB_CREATE_DB = False`` if you manage database schema manually
2. Keep default ``True`` value for automatic table creation (existing behavior)
3. Use this setting to control database initialization in different environments

**13. Dependency Changes**

**Removed Dependencies:**
- ``flask-mongoengine``
- ``mongoengine``
- ``pymongo``
- ``flask-openid``

**Updated Dependencies:**
- SQLAlchemy 1.4+ or 2.x support
- Flask-SQLAlchemy 2.x or 3.x support

**Migration Steps:**
1. Remove MongoDB and OpenID dependencies from requirements.txt
2. Update SQLAlchemy and Flask-SQLAlchemy versions
3. Install updated dependencies: ``pip install -r requirements.txt``

**Testing Your Migration**

After completing the migration:

1. **Database Setup**: Ensure your SQL database is properly configured
2. **Authentication Test**: Verify login works with your chosen auth method
3. **View Testing**: Test all your ModelView-based views
4. **API Testing**: If using REST APIs, verify they work correctly
5. **Run Tests**: Execute your test suite to catch any remaining issues

**Getting Help**

If you encounter issues during migration:

1. Check the `Flask-AppBuilder GitHub issues <https://github.com/dpgaspar/Flask-AppBuilder/issues>`_
2. Review the `Flask-AppBuilder documentation <https://flask-appbuilder.readthedocs.io/>`_
3. For SQLAlchemy 2.x specific issues, consult the `SQLAlchemy migration guide <https://docs.sqlalchemy.org/en/20/changelog/migration_20.html>`_

Migrating to 1.9.0
------------------

If you are using OAuth for authentication, this release will break your logins. This break is due to two reasons

One:


There was a security issue when using the default builtin information getter for the providers
(see github: Prevent masquerade attacks through oauth providers #472)
This fix will prepend the provider to the user id. So your usernames will look like 'google_<USER_ID>'

Two:


For google OAuth we migrated from the old and deprecated google plus API to OAuth2/v2, the old User.username field
was based on the Google Plus display name, and now is based on a Google user_id.


In order to upgrade without breaking, you can override the current default OAuth information getter using something like this::


    @appbuilder.sm.oauth_user_info_getter
    def get_oauth_user_info(sm, provider, response=None):
    # for GITHUB
        if provider == 'github' or provider == 'githublocal':
            me = sm.oauth_remotes[provider].get('user')
            return {'username': me.data.get('login')}
        # for twitter
        if provider == 'twitter':
            me = sm.oauth_remotes[provider].get('account/settings.json')
            return {'username': me.data.get('screen_name', '')}
        # for linkedin
        if provider == 'linkedin':
            me = sm.oauth_remotes[provider].get('people/~:(id,email-address,first-name,last-name)?format=json')
            return {'username': me.data.get('id', ''),
                    'email': me.data.get('email-address', ''),
                    'first_name': me.data.get('firstName', ''),
                    'last_name': me.data.get('lastName', '')}
        # for Google
        if provider == 'google':
            me = sm.oauth_remotes[provider].get('userinfo')
            return {'username': me.data.get('id', ''),
                    'first_name': me.data.get('given_name', ''),
                    'last_name': me.data.get('family_name', ''),
                    'email': me.data.get('email', '')}


There was a Fix for the **oauth_user_info_getter** decorator also, now it will obey the doc definition.

Any help you need feel free to submit an Issue!


Migrating to 1.8.0
------------------

On this release flask-appbuilder supports python 3.5, and returned to flask-babel original package
(stopped using the fork flask-babelpkg for multiple translation directories).

You can and should, uninstall flask-babelpkg from your package list and change all your imports from::

    from flask_babelpkg import ...

To::

    from flask_babel import ...



Migrating from 1.2.X to 1.3.X
------------------------------

There are some breaking features:

1 - Security models have changed, users can have multiple roles, not just one. So you have to upgrade your db.

- The security models schema have changed.

    If you are using sqlite, mysql, pgsql, mssql or oracle, use the following procedure:

        1 - *Backup your DB*.

        2 - If you haven't already, upgrade to flask-appbuilder 1.3.0.

        3 - Issue the following commands, on your project folder where config.py exists::

            $ cd /your-main-project-folder/
            $ fabmanager upgrade-db

        4 - Test and Run (if you have a run.py for development) ::

            $ fabmanager run

    For **sqlite** you'll have to drop role_id columns and FK yourself. follow the script instructions to finish the upgrade.


2 - Security. If you were already extending security, this is even more encouraged from now on, but internally many things have
changed. So, modules have changes and changed place, each backend engine will have it's SecurityManager, and views
are common to all of them. Change:

from::

    from flask_appbuilder.security.sqla.views import UserDBModelView
    from flask_appbuilder.security.manager import SecurityManager


to::

    from flask_appbuilder.security.views import UserDBModelView
    from flask_appbuilder.security.sqla.manager import SecurityManager

3 - SQLAInteface, SQLAModel. If you were importing like the following, change:

from::

    from flask_appbuilder.models import SQLAInterface

to::

    from flask_appbuilder.models.sqla.interface import SQLAInterface

4 - Filters, filters import moved::

to::

    from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction, FilterEqual

5 - Filters, filtering relationship fields (rendered with select2) changed:

from::

    edit_form_query_rel_fields = [('group',
                                   SQLAModel(Model1, self.db.session),
                                   [['field_string', FilterEqual, 'G2']]
                                  )
                                ]

to::

    edit_form_query_rel_fields = {'group':[['field_string', FilterEqual, 'G2']]}



Migrating from 1.1.X to 1.2.X
------------------------------

There is a breaking feature, change your filters imports like this:

from::

    flask_appbuilder.models.base import Filters, BaseFilter, BaseFilterConverter
    flask_appbuilder.models.filters import FilterEqual, FilterRelation ....

to::

    flask_appbuilder.models.filters import Filters, BaseFilter, BaseFilterConverter
    flask_appbuilder.models.sqla.filter import FilterEqual, FilterRelation ....


Migrating from 0.9.X to 0.10.X
------------------------------

This new version has NO breaking features, all your code will work, unless you are hacking directly onto SQLAModel,
Filters, DataModel etc.

But, to keep up with the changes, you should change these:

::

    from flask_appbuilder.models.datamodel import SQLAModel
    from flask_appbuilder.models.filters import FilterEqual, FilterContains
to::

    from flask_appbuilder.models.sqla.interface import SQLAInterface
    from flask_appbuilder.models.sqla.filters import FilterEqual, FilterContains



Migrating from 0.8.X to 0.9.X
-----------------------------

This new version has a breaking feature, the way you initialize AppBuilder (former BaseApp) has changed.
internal retro compatibility was created, but many things have changed

1 - Initialization of AppBuilder (BaseApp) has changed, pass session not SQLAlchemy *db* object.
this is the breaking feature.

    from (__init__.py) ::

        BaseApp(app, db)

    to (__init__.py) ::

        AppBuilder(app, db.session)


2 - 'BaseApp' changed to 'AppBuilder'. Has you already noticed on 1.

3 - BaseApp or now AppBuilder will not automatically create your models, after declaring them just invoke create_db method::

    appbuilder.create_db()

4 - Change your models inheritance

    from::

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            first_name = Column(String(64), nullable=False)

    to::

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            first_name = Column(String(64), nullable=False)

5 - Although you're not obligated, you should not directly use your flask.ext.sqlalchemy class SQLAlchemy.
Use F.A.B. SQLA class instead, read the docs to know why.

    from (__init__.py)::

        from flask import Flask
        from flask.ext.sqlalchemy import SQLAlchemy
        from flask_appbuilder.baseapp import BaseApp


        app = Flask(__name__)
        app.config.from_object('config')
        db = SQLAlchemy(app)
        baseapp = BaseApp(app, db)

    to (__init__.py)::

        from flask import Flask
        from flask_appbuilder import SQLA, AppBuilder

        app = Flask(__name__)
        app.config.from_object('config')
        db = SQLA(app)
        appbuilder = AppBuilder(app, db.session)



Migrating from 0.6.X to 0.7.X
-----------------------------

This new version has some breaking features. You don't have to change any code, main breaking changes are:

 - The security models schema have changed.

    If you are using sqlite, mysql or pgsql, use the following procedure:

        1 - *Backup your DB*.

        2 - If you haven't already, upgrade to flask-appbuilder 0.7.0.

        3 - Issue the following commands, on your project folder where config.py exists::

            cd /your-main-project-folder/
            wget https://raw.github.com/dpgaspar/Flask-AppBuilder/master/bin/migrate_db_0.7.py
            python migrate_db_0.7.py
            wget https://raw.github.com/dpgaspar/Flask-AppBuilder/master/bin/hash_db_password.py
            python hash_db_password.py

        4 - Test and Run (if you have a run.py for development) ::

            python run.py

    If not (DB is not sqlite, mysql or pgsql), you will have to alter the schema yourself. use the following procedure:

        1 - *Backup your DB*.

        2 - If you haven't already, upgrade to flask-appbuilder 0.7.0.

        3 - issue the corresponding DDL commands to:

        ALTER TABLE ab_user MODIFY COLUMN password VARCHAR(256)

        ALTER TABLE ab_user ADD COLUMN login_count INTEGER

        ALTER TABLE ab_user ADD COLUMN created_on DATETIME

        ALTER TABLE ab_user ADD COLUMN changed_on DATETIME

        ALTER TABLE ab_user ADD COLUMN created_by_fk INTEGER

        ALTER TABLE ab_user ADD COLUMN changed_by_fk INTEGER

        ALTER TABLE ab_user ADD COLUMN last_login DATETIME

        ALTER TABLE ab_user ADD COLUMN fail_login_count INTEGER

        4 - Then hash your passwords::

            wget https://raw.github.com/dpgaspar/Flask-AppBuilder/master/bin/hash_db_password.py
            python hash_db_password.py

 - All passwords are kept on the database hashed, so all your passwords will be hashed by the framework.

 - Please *backup* your DB before altering the schema,  if you feel lost please post an issue on github
    https://github.com/dpgaspar/Flask-AppBuilder/issues?state=open


Migrating from 0.5.X to 0.6.X
-----------------------------

This new version has some breaking features, that I hope will be easily changeable on your code.

If you feel lost please post an issue on github: https://github.com/dpgaspar/Flask-AppBuilder/issues?state=open

If you're using the **related_views** attribute on ModelView classes, you must not instantiate the related classes. This is the correct form, it will be less memory and cpu resource consuming.

From this::


    class MyView(GeneralView):
        datamodel = SQLAModel(Group, db.session)
        related_views = [MyOtherView()]


Change to this::

  
    class MyView(GeneralView):
        datamodel = SQLAModel(Group, db.session)
        related_views = [MyOtherView]


Migrating from 0.2.X to 0.3.X
-----------------------------

This new version (0.3.X) has many internal changes, if you feel lost please post an issue on github
https://github.com/dpgaspar/Flask-AppBuilder/issues?state=open

All direct imports from your 'app' directory were removed, so there is no obligation in using the base AppBuilder-Skeleton.

Security tables have changed their names, AppBuilder will automatically migrate all your data to the new tables.

1 - Change your BaseApp initialization (views.py)

From this::

	baseapp = BaseApp(app)

Change to this::

	baseapp = BaseApp(app, db)
	
2 - Remove from OpenID and Login initialization (__init__.py)

From this::

	app = Flask(__name__)
	app.config.from_object('config')
	db = SQLAlchemy(app)
	babel = Babel(app)
	lm = LoginManager()
	lm.init_app(app)
	lm.login_view = 'login'
	oid = OpenID(app, os.path.join(basedir, 'tmp'))
	
	from app import models, views
	
Change to this::

	app = Flask(__name__)
	app.config.from_object('config')
	db = SQLAlchemy(app)
	
	from app import models, views


Migrating from 0.1.X to 0.2.X
-----------------------------

It's very simple, change this::

	baseapp = BaseApp(app)
	baseapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
	baseapp.add_view(PersonGeneralView, "List Contacts","/persons/list","earphone","Contacts")
	baseapp.add_view(PersonChartView, "Contacts Chart","/persons/chart","earphone","Contacts")
	
To this::

	baseapp = BaseApp(app)
	baseapp.add_view(GroupGeneralView(), "List Groups","/groups/list","th-large","Contacts")
	baseapp.add_view(PersonGeneralView(), "List Contacts","/persons/list","earphone","Contacts")
	baseapp.add_view(PersonChartView(), "Contacts Chart","/persons/chart","earphone","Contacts")

Small change, you just have to instantiate your classes.


