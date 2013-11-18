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

First let's create a very simple *Group* table to group our contacts

Define your models (models.py)
------------------------------

::

        class Group(BaseMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique = True, nullable=False)

            def __repr__(self):
                return self.name


Define your Views (views.py)
----------------------------

Now we are going to define our view to *Group* table

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

I hope this was easy enough! Some questions may arrise.


Register (views.py)
--------

Register everything, to present the models and create the menu::

        genapp = BaseApp(app)
        genapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
        genapp.add_view(ContactGeneralView, "List Contacts","/contacts/list","earphone","Contacts")

