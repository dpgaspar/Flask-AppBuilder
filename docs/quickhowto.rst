Quick How to
============

The Base Skeleton Application
-----------------------------

If your working with the base skeleton application (see 3 step instalation)

you now have the following directory structure::

    <your project name>/
        config.py : All the applications configuration
        run.py    : A runner mainly for debug
        app/
            __init__.py : Application's initialization
            models.py : Declare your database models here
            views.py  : Implement your views here

    
It's very easy and fast to create an application out of the box, with detailed security.

Please take a look at github examples on:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples

Simple contacts application
---------------------------

Lets create a very simple contacts application.

First let's create a *Group* table to group our contacts

Define your models (models.py)
------------------------------

The group table.

::

        class Group(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique = True, nullable=False)

            def __repr__(self):
                return self.name

An *Contacts* table.

::

	class Contact(db.Model):
	    id = db.Column(db.Integer, primary_key=True)
	    name =  db.Column(db.String(150), unique = True, nullable=False)
	    address =  db.Column(db.String(564))
	    birthday = db.Column(db.Date)
	    personal_phone = db.Column(db.String(20))
	    personal_celphone = db.Column(db.String(20))
	    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	    group = db.relationship("Group")	
	    
	    def __repr__(self):
                return self.name	


Define your Views (views.py)
----------------------------

Now we are going to define our view to *Group* table

::
  
        class GroupGeneralView(GeneralView):
    		datamodel = SQLAModel(Group, db.session)
    		related_views = [ContactGeneralView()]

    		list_columns = ['name']
    		order_columns = ['name']
    		search_columns = ['name']

I hope this was easy enough! Some questions may arrise...

Must have properties:

- datamodel: is the db abstraction layer. Initialize it with your model and sqlalchemy session
- list_columns: The columns that will be displayed on the list view.
- order_columns: The columns allowed to be ordered (to not define relations on this)
- search_columns: The columns that will display on the search form.

Optional properties:

- related_views: if you want a master/detail view on the show and edit.

There are many more properties you can override to customize your views. you can define descriptions for columns, validators for forms, and many more

Take a look at the Views chapter.


But where is ContactGeneralView ?

Let's define it::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)

        label_columns = {'group':'Contacts Group'}
        list_columns = ['name','personal_celphone','birthday','group']

        order_columns = ['name','personal_celphone','birthday']
        search_columns = ['name','personal_celphone','group']

        show_fieldsets = [
            ('Summary',{'fields':['name','address','group']}),
            ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
            ]

Some explanation:

- label_columns: defines your labels for columns (dha!). The framework will define the missing ones for you, with a pretty version of your column names.
- show_fieldsets: A fieldset (Django style).


Register (views.py)
-------------------

Register everything, to present the models and create the menu::

        genapp = BaseApp(app)
        genapp.add_view(GroupGeneralView(), "List Groups",icon = "th-large",category = "Contacts")
        genapp.add_view(ContactGeneralView(), "List Contacts",icon = "earphone",category = "Contacts")

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Some images:

.. image:: ./images/login.png
    :width: 100%

.. image:: ./images/group_list.png
    :width: 100%

.. image:: ./images/contact_list.png
    :width: 100%

    
