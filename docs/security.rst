Security
========

The Authentication methods
--------------------------

You have three types of authentication methods

	- Database type authentications: username and password style that is queried from the database to match, atention this framework does not encrypt (yet...) the passwords.
	
	- Open ID: Uses the user's email field to authenticate on Gmail, Yahoo etc...

	- LDAP: Authentication against an LDAP server, like Microsoft Active Directory.

Configure the authentication type on config take a look :doc:`config`

The session is preserved and encrypted using Flask-Login, OpenID requires Flask-OpenID.

Role based
----------

Each user belong's to a role, and a role holds permissions on views and menus, so a user has permissions on views and menus.

There are two special roles, you can define their names on the :doc:`config`

	- Admin Role: The framework will assign all the existing permission on views and menus to this role, automatically, this role is for authenticated users only.	 

	- Public Role: This is a special role for non authenticated users, you can assign all the permissions on views and menus to this role, and everyone will access specific parts of you application.
	
Of course you can create any aditional role you want and configure them as you like.

Permissions
-----------

The framework you automatically create all the possible existing permissions on your views or menus, by "inspection" your code. 

Each time you create a new view based on a model (inherit from GeneralView) it will create the following permissions:

	- can list
	- can show
	- can add
	- can edit
	- can delete
	- can download
	
These base permission will be associated with your view, so if you create a view named "MyGeneralView" you can assign to any role these permissions:

	- can list on MyGeneralView
	- can show on MyGeneralView
	- can add on MyGeneralView
	- can edit on MyGeneralView
	- can delete on MyGeneralView
	- can doanload on MyGeneralView
	
If you extend your view with some exposed method via the @expose decorator::

	class MyGeneralView(GeneralView):
    		datamodel = SQLAModel(Group, db.session)
    	
    		list_columns = ['name']
    		show_columns = ['name']
    		order_columns = ['name']
    		search_columns = ['name']
    	
    		@expose('/mymethod/')
		@has_access
		def mymethod(self):
			# do something
			pass
    	
The framework will create the following access:

	- can mymethod on MyGeneralView
	
And the decorator @has_access will prevent any unwanted access

Some images:

.. image:: ./images/security.png
    :width: 100%
