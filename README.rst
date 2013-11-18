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

4 Steps to get Started
----------------------

- Install it::

	pip install flask-appbuilder
	git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git


- Configure it::

	python init_app.py

- Run it::

	python run.py


That's it!!


Some Explanation
................

init_app.py has created:

    - A fresh new database.
    - The security tables and all your application tables too.
    - 'admin' user associated with role "Admin".
    - all your applications detailed permissions.
    - All permission to Role "Admin" (AUTH_ROLE_ADMIN).

The 'admin' password will be 'general'. Change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')


Base Configuration
..................

Use config.py to configure the following parameters. By default it will use SQLLITE DB, and bootstrap 3.0.0 base theme:

  - SQLALCHEMY_DATABASE_URI: Database connection string
  - AUTH_TYPE: This is the authentication type
	- 0 = Open ID
	- 1 = Database style (user/password)
  - AUTH_ROLE_ADMIN: Configure the name of the admin role. 
  - AUTH_ROLE_PUBLIC: Special Role that holds the public permissions, no authentication needed
  - APP_NAME: The name of your application
  - APP_THEME: Various themes for you to choose from (bootwatch).

How to do it?
-------------

It's very easy and fast to create an application out of the box, with detailed security.

Please take a look at github examples on:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples


Define your models (models.py)
..............................

::

        class Group(BaseMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique = True, nullable=False)

            def __repr__(self):
                return self.name

        class Contact(AuditMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(150), unique = True, nullable=False)
            address = db.Column(db.String(564))
            birthday = db.Column(db.Date)
            photo = db.Column(ImageColumn, nullable=False )
            group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
            group = db.relationship("Group")
            
            def __repr__(self):
                return self.name



Define your Views (views.py)
............................

Notice the 'fieldset' that is only defined on the show view.
You can define them to add or edit also, in any diferent way.

Notice also the 'related_views', will show a master/detail on
the 'group show view' and 'edit show view' listing the related contacts

::
  
        class GroupGeneralView(GeneralView):
            route_base = '/groups'
            datamodel = SQLAModel(Group, db.session)
            related_views = [ContactGeneralView()]

            list_title = 'List Groups'
            show_title = 'Show Group'
            add_title = 'Add Group'
            edit_title = 'Edit Group'

            label_columns = { 'name':'Name'}
            list_columns = ['name']
            show_columns = ['name']
            order_columns = ['name']
            search_columns = ['name']
    
        class ContactGeneralView(GeneralView):
            route_base = '/contacts'
            datamodel = SQLAModel(Contact, db.session)

            list_title = 'List Contacts'
            show_title = 'Show Contacts'
            add_title = 'Add Contact'
            edit_title = 'Edit Contact'

            label_columns = {'name':'Name',
                        'photo':'Photo',
                        'photo_img':'Photo',
                        'address':'Address',
                        'birthday':'Birthday',
                        'group':'belongs to group'}                
            description_columns = {'name':'The Contacts Name'}
            list_columns = ['name','group']
            show_fieldsets = [
                 ('Summary',{'fields':['photo_img','name','address','group']}),
                 ('Personal Info',{'fields':['birthday'],'expanded':False}),
                 ]
            order_columns = ['name']
            search_columns = ['name']

        baseapp = BaseApp(app)
        baseapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
        baseapp.add_view(ContactGeneralView, "List Contacts","/contacts/list","earphone","Contacts")


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

