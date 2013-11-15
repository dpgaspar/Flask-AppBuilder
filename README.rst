Flask App Builder
=================

Simple and rapid Application builder, includes detailed security, auto form generation, google charts and much more.


Includes:
---------

  - Security
        - Auto permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
        - Inserts on the Database all the detailed permissions possible on your application.
        - Public (no authentication needed) and Private permissions.
        - Role based permissions.
        - Authentication based on OpenID and Database (Planning LDAP).
  - Views and Widgets
	- Auto menu generator.
	- Various view widgets: lists, master-detail, list of thumbnails etc
	- Select2, Datepicker, DateTimePicker
	- Menu with icons
	- Google charts with automatic group by.
  - Forms
	- Auto Create, Remove, Add, Edit and Show from Database Models
	- Labels and descriptions for each field
	- Image and File support for upload and database field association. It will handle everything for you.
	- Field sets for Form's (Django style).
  - i18n
	- Support for multi-language via Babel (still not working in package form)
  - Bootstrap 3.0.0 CSS and js, with Select2 and DatePicker

Instalation
-----------

This is finally on PyPi. So for easy instalation::

    pip install flask-appbuilder

for your first application you can use "skeleton" or "examples/simpleapp" 

Initial configuration
.....................

After having the initial skeleton of your app, initialize the database::

    python init_app.py

Use init_app.py (folder 'bin' on git) will create a fresh new database.
Add an 'admin' associated with role "Admin" with all permissions.
The 'admin' password will be 'general' change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')

Base Configuration
..................

Use config.py to configure the following parameters, by default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

  - Database connection string (SQLALCHEMY_DATABASE_URI)
  - AUTH_TYPE: This is the authentication type
	- 0 = Open ID
	- 1 = Database style (user/password)
  - AUTH_ROLE_ADMIN: Configure the name of the admin role. All you new models and view will have automatic full access on this role
  - AUTH_ROLE_PUBLIC: Special Role that holds the public permissions, no authentication needed
  - APP_NAME: The name of your application
  - APP_THEME: Various themes for you to choose from (bootwatch).

How to do it?
-------------

It's very easy and fast to create an application out of the box, with detailed security

Please take a look at github examples on: 

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples


Define your models (models.py)
..............................

::

        class Group(db.Model):
            id = db.Column(db.Integer, primary_key = True)
            name =  db.Column(db.String(264), 
							unique = True, nullable=False)
            address =  db.Column(db.String(564))
            phone1 = db.Column(db.String(50))
            phone2 = db.Column(db.String(50))
            taxid = db.Column(db.Integer)
            notes = db.Column(db.String(550))

            def __repr__(self):
                return self.name


Define your Views (views.py)
............................

::

        class GroupGeneralView(GeneralView):
                route_base = '/groups'
                datamodel = SQLAModel(Group, db.session)

                list_title = 'List Groups'
                show_title = 'Show Group'
                add_title = 'Add Group'
                edit_title = 'Edit Group'

                label_columns = { 'name':'Name','address':'Address',
					'phone1':'Phone (1)',
					'phone2':'Phone (2)',
					'taxid':'Tax ID',
					'notes':'Notes'}
                description_columns = {'name':'Write this group name'}
                list_columns = ['name','notes']
                show_columns = ['name','address','phone1','phone2','taxid','notes']
                order_columns = ['name','notes']
                search_columns = ['name']

	
        genapp = General(app)
        genapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")


Some pictures
-------------

Master Detail view with related lists:

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/master_detail_list.png "List"

Login page (with AUTH_DB):

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login.png "Login"

Charts:

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/Charts.png "Charts"

Pictures in List Thumbnail:

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/ListThumbnail.png

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

