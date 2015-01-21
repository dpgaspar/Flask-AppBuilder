Security
========

Supported Authentication Types
------------------------------

You have four types of authentication methods

  :Database Authentication: username and password style that is queried from the database to match. Passwords are kept hashed on the database.
  :Open ID: Uses the user's email field to authenticate on Gmail, Yahoo etc...
  :LDAP: Authentication against an LDAP server, like Microsoft Active Directory.
  :REMOTE_USER: Reads the *REMOTE_USER* web server environ var, and verifies if it's authorized with the framework users table.
       It's the web server responsibility to authenticate the user, useful for intranet sites, when the server (Apache, Nginx)
       is configured to use kerberos, no need for the user to login with username and password on F.A.B.

Configure the authentication type on config.py, take a look at :doc:`config`

The session is preserved and encrypted using Flask-Login, OpenID requires Flask-OpenID.

Role based
----------

Each user has multiple roles, and a role holds permissions on views and menus, so a user has permissions on views and menus.

There are two special roles, you can define their names on the :doc:`config`

	:Admin Role: The framework will assign all the existing permission on views and menus to this role, automatically, this role is for authenticated users only.

	:Public Role: This is a special role for non authenticated users, you can assign all the permissions on views and menus to this role, and everyone will access specific parts of you application.
	
Of course you can create any additional role you want and configure them as you like.

.. notes:: User's with multiple roles is only possible since 1.3.0 version.

Permissions
-----------

The framework automatically creates for you all the possible existing permissions on your views or menus, by "inspecting" your code.

Each time you create a new view based on a model (inherit from ModelView) it will create the following permissions:

	- can list
	- can show
	- can add
	- can edit
	- can delete
	- can download
	
These base permissions will be associated to your view, so if you create a view named "MyModelView" you can assign to any role these permissions:

	- can list on MyModelView
	- can show on MyModelView
	- can add on MyModelView
	- can edit on MyModelView
	- can delete on MyModelView
	- can doanload on MyModelView
	
If you extend your view with some exposed method via the @expose decorator and you want to protect it
use the @has_access decorator::

    class MyModelView(ModelView):
        datamodel = SQLAInterdace(Group)
    	
        @has_access
        @expose('/mymethod/')
        def mymethod(self):
            # do something
            pass

The framework will create the following access based on your method's name:

	- can mymethod on MyModelView
	
You can aggregate some of your method's on a single permission, this can simplify the security configuration
if there is no need for granular permissions on a group of methods, for this use @permission_name decorator.

You can use the @permission_name to override the permission's name to whatever you like.

Take a look at :doc:`api`

Automatic Cleanup
-----------------

All your permissions and views are added automatically to the backend and associated with the 'Admin' *role*.
The same applies to removing them. But, if you change the name of a view or menu, the framework
will add the new *Views* and *Menus* names to the backend, but will not delete the old ones. It will generate unwanted
names on the security models, basically *garbage*. To clean them, use the *security_cleanup* method.

Using security_cleanup is not always necessary, but using it after code rework, will guarantee that the permissions, and
associated permissions to menus and views are exactly what exists on your app. It will prevent orphaned permission names
 and associations.

Use the cleanup after you have registered all your views.
::

    appbuilder.add_view(GroupModelView, "List Groups", category="Contacts")
    appbuilder.add_view(ContactModelView, "List Contacts", category="Contacts")
    appbuilder.add_separator("Contacts")
    appbuilder.add_view(ContactChartView, "Contacts Chart", category="Contacts")
    appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", category="Contacts")

    appbuilder.security_cleanup()


You can always use it and everything will be painlessly automatic. But if you use it only when needed
(change class name, add to *security_cleanup* to your code, the *garbage* names are removed, then remove the method)
no overhead is added when starting your site.

Auditing
--------

All user's creation and modification are audited.
On the show detail for each user you can check who created the user and when and who has last changed it.

You can check also, a total login count (successful login), and the last failed logins
(these are reset if a successful login occurred).

Your Custom Security
--------------------

If you want to alter the security views, or authentication methods since (1.0.1) you can do it in a simple way.
The **AppBuilder** has a new optional initialization parameter where you pass your own custom **SecurityManager**
If you want to add, for example, actions to the list of users you can do it in a simple way.

First i advise you to create security.py and add the following to it::

    from flask import redirect
    from flask_appbuilder.security.views import UserDBModelView
    from flask_appbuilder.security.sqla.manager import SecurityManager
    from flask.ext.appbuilder.actions import action


    class MyUserDBView(UserDBModelView):
        @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
        def muldelete(self, items):
            self.datamodel.delete_all(items)
            self.update_redirect()
            return redirect(self.get_redirect())


    class MySecurityManager(SecurityManager):
        userdbmodelview = MyUserDBView

Then on the __init__.py initialize AppBuilder with you own security class::

    appbuilder = AppBuilder(app, db.session, security_manager_class=MySecurityManager)


F.A.B. uses a different user view for each authentication method

 - UserDBModelView - for database auth method
 - UserOIDModelView - for Open ID auth method
 - UserLDAPModelView - for LDAP auth method

You can extend or create from scratch your own, and then tell F.A.B. to use them instead, by overriding their
correspondent lower case properties on **SecurityManager** (just like on the given example).

Take a look and run the example on `Employees example <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/employees>`_

Study the source code of `BaseSecurityManager <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/security/manager.py>`_

Extending the User Model
------------------------

If you want to extend the **User** Model with extra columns specific to your application (since 1.3.0) you
can easily do it. Use the same type of approach as explained earlier.

First extend the User Model (create a sec_models.py file)::

    from flask_appbuilder.security.sqla.models import User
    from sqlalchemy import Column, Integer, ForeignKey, String, Sequence, Table
    from sqlalchemy.orm import relationship, backref
    from flask_appbuilder import Model

    class MyUser(User):
        extra = Column(String(256))


Next define a new User view, just like the default User view but with the extra column (create a sec_view.py)::

    from flask_appbuilder.security.views import UserDBModelView
    from flask_babelpkg import lazy_gettext

    class MyUserDBModelView(UserDBModelView):
        """
            View that add DB specifics to User view.
            Override to implement your own custom view.
            Then override userdbmodelview property on SecurityManager
        """

        show_fieldsets = [
            (lazy_gettext('User info'),
             {'fields': ['username', 'active', 'roles', 'login_count', 'extra']}),
            (lazy_gettext('Personal Info'),
             {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
            (lazy_gettext('Audit Info'),
             {'fields': ['last_login', 'fail_login_count', 'created_on',
                         'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
        ]

        user_show_fieldsets = [
            (lazy_gettext('User info'),
             {'fields': ['username', 'active', 'roles', 'login_count', 'extra']}),
            (lazy_gettext('Personal Info'),
             {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
        ]

        add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'roles', 'extra', 'password', 'conf_password']
        list_columns = ['first_name', 'last_name', 'username', 'email', 'active', 'roles']
        edit_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'roles', 'extra']

Next create your own SecurityManager class, overriding your model and view for User (create a sec.py)::

    from flask_appbuilder.security.sqla.manager import SecurityManager
    from .sec_models import MyUser
    from .sec_views import MyUserDBModelView

    class MySecurityManager(SecurityManager):
        user_model = MyUser
        userdbmodelview = MyUserDBModelView

Finally (as shown on the previous example) tell F.A.B. to use your SecurityManager class, so when initializing
**AppBuilder** (on __init__.py)::

    from flask import Flask
    from flask.ext.appbuilder import SQLA, AppBuilder
    from flask.ext.appbuilder.menu import Menu
    from .sec import MySecurityManager

    app = Flask(__name__)
    app.config.from_object('config')
    db = SQLA(app)
    appbuilder = AppBuilder(app, db.session, menu=Menu(reverse=False), security_manager_class=MySecurityManager)

    from app import views

Now you'll have your extended User model as the authenticated user, *g.user* will have your model with the extra col.

Some images:

.. image:: ./images/security.png
    :width: 100%
