Security
========

The Authentication methods
--------------------------

You have three types of authentication methods

	- Database type authentications: username and password style that is queried from the database to match. Passwords are kept hashed on the database.
	
	- Open ID: Uses the user's email field to authenticate on Gmail, Yahoo etc...

	- LDAP: Authentication against an LDAP server, like Microsoft Active Directory.

Configure the authentication type on config.py, take a look at :doc:`config`

The session is preserved and encrypted using Flask-Login, OpenID requires Flask-OpenID.

Role based
----------

Each user belongs to a role, and a role holds permissions on views and menus, so a user has permissions on views and menus.

There are two special roles, you can define their names on the :doc:`config`

	- Admin Role: The framework will assign all the existing permission on views and menus to this role, automatically, this role is for authenticated users only.	 

	- Public Role: This is a special role for non authenticated users, you can assign all the permissions on views and menus to this role, and everyone will access specific parts of you application.
	
Of course you can create any additional role you want and configure them as you like.

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
        datamodel = SQLAModel(Group, db.session)
    	
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
The same applies to removing them, to some extent. But, if you change the name of a view or menu the framework
will add the new *Views* and *Menus* names to the backend, but, will not delete the old ones. This can generate unwanted
names on the security basically *garbage*. To clean it use the *security_cleanup* method,
use it after you have registered all your views

::

    appbuilder.add_view(GroupModelView(), "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
    appbuilder.add_view(ContactModelView(), "List Contacts", icon="fa-envelope", category="Contacts")
    appbuilder.add_separator("Contacts")
    appbuilder.add_view(ContactChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts")
    appbuilder.add_view(ContactTimeChartView(), "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

    appbuilder.security_cleanup()


You can always use it and everything will be painlessly automatic. But if you use it only when needed
(change class name, add to *security_cleanup* to your code, the *garbage* names are removed, then remove the method)
no overhead is added when starting your site.

Auditing
--------

All user's creation and modification are audited, on the show detail for each user you can check who created the user and when and who has last changed it.

You can check also a total login count (successful login), and the last failed logins (these are reset if a successful login then occurred).


Your Custom Security
--------------------

If you want to alter the security views, or authentication methods since (1.0.1) you can do it in a simple way.
The **AppBuilder** has a new optional initialization parameter where you pass your own custom **SecurityManager**
If you want to add, for example, actions to the list of users you can do it in a simple way.

First i advise you to create security.py and add the following to it::

    from flask import redirect
    from flask_appbuilder.security.views import UserDBModelView
    from flask_appbuilder.security.manager import SecurityManager
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

Study the source code of `SecurityManager <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/security/manager.py>`_

Some images:

.. image:: ./images/security.png
    :width: 100%
