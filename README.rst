Flask App Builder
=================

Simple and rapid Application builder, includes detailed security, auto form generation, google charts and much more.


Includes:
---------

  - Auto Create, Remove, Add, Edit and Show from Database Models
  - Support for multi-language via Babel
  - Auto File and Image with extended SQLA types, and auto upload form field creation.
  - Filter lists with configurable search form, including related fields (Select box).
  - Auto WTForm generator, with select (single and multiple) and DatePicker.
  - Field set's for Form's (Django style).
  - Google charts with automatic group by's.
  - Easy to extend via big widget's like charts, master-detail lists, etc...
  - Auto menu generator.
  - Security (OID, DB), detailed permissions on menus, create, edit, remove, show.
  - User's, Role, and detail permission automaticaly created on the DB.
  - Public and private permissions
  - Bootstrap 3.0.0 CSS and js, with Select2 and DatePicker

Instalation
-----------

This is finally on PyPi. So for easy instalation::

    pip install flask-appbuilder

for your first application you can use "skeleton" ou "examples/simpleapp" 

Initial configuration
---------------------

After having the initial skeleton of you app, initialize the database.

Use init_app.py (folder scripts on git) will create a fresh new database, and add an 'admin' user with all permissions.
The 'admin' password will be 'general' change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')

Base Configuration
------------------

Use config.py to configure the following parameters, by default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

  - Database connection string (SQLALCHEMY_DATABASE_URI)
  - AUTH_TYPE: This is the authentication type
	- 0 = Open ID
	- 1 = Database style (user/password)
  - AUTH_ROLE_ADMIN: Configure the name of the admin role. All you new models and view will have automatic full access on this role
  - APP_NAME: The name of your application
  - APP_THEME: Various themes for you to choose from (bootwatch).

How to do it?
-------------

It's very easy and fast to create an application out of the box, with detailed security:

Define your models (models.py):
-------------------------------

.. code-block:: python
        class Group(db.Model):
            id = db.Column(db.Integer, primary_key = True)
            name =  db.Column(db.String(264), unique = True, nullable=False)
            address =  db.Column(db.String(564))
            phone1 = db.Column(db.String(50))
            phone2 = db.Column(db.String(50))
            taxid = db.Column(db.Integer)
            notes = db.Column(db.String(550))

            def __repr__(self):
                return self.name


Define your Views (views.py):
---------------------------------

.. code-block:: python
        class GroupGeneralView(GeneralView):
                route_base = '/groups'
                datamodel = SQLAModel(Group)
                decorators = [login_required]

                list_title = 'List Groups'
                show_title = 'Show Group'
                add_title = 'Add Group'
                edit_title = 'Edit Group'

                label_columns = { 'name':'Name','address':'Address','phone1':'Phone (1)','phone2':'Phone (2)','taxid':'Tax ID','notes':'Notes'}
                description_columns = {'name':'Write this group name'}
                list_columns = ['name','notes']
                show_columns = ['name','address','phone1','phone2','taxid','notes']
                order_columns = ['name','notes']
                search_columns = ['name']

	
        genapp = General(app, Menu())
        genapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")


Some pictures
-------------

Master Detail view with related lists:

https://raw.github.com/dpgaspar/homeapp/master/master_detail_list.png "List"

Login page (with AUTH_DB):

https://raw.github.com/dpgaspar/homeapp/master/login.png "Login"

Depends on:
-----------

- flask
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel

Planning to include:
--------------------
 
 - Security for ldap auth.
 - Easy page flow definition (wizard style).
 
This is not production ready.

