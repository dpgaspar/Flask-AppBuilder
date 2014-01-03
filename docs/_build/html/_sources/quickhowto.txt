Quick How to
============

The Base Skeleton Application
-----------------------------

If your working with the base skeleton application :doc:`instalation`

you now have the following directory structure::

    <your project name>/
        config.py : All the applications configuration
        run.py    : A runner mainly for debug
        app/
            __init__.py : Application's initialization
            models.py : Declare your database models here
            views.py  : Implement your views here

    
It's very easy and fast to create an application out of the box, with detailed security.

Please take a look at github `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_


Simple contacts application
---------------------------

Lets create a very simple contacts application.

First we are going to create a *Group* table, to group our contacts

.. note::
	Since version 0.3.9 i advise not using Flask-SqlAlchemy to define your tables, because you will be in a diferent declarative model of the security tables from AppBuilder.
	If you want to use AuditMixin :doc:`api` or include a relation to a User or login User you must be on the same declarative base.
	Use BaseMixin to have automatic table name baptism like in Flask-SqlAlchemy, and inherit also from Base, that you import::

		flask.ext.appbuilder import Base
	

Define your models (models.py)
------------------------------

The group table.

::

        class Group(BaseMixin, Base):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

            def __repr__(self):
                return self.name

An *Contacts* table.

::

	class Contact(BaseMixin, Base):
	    id = Column(Integer, primary_key=True)
	    name =  Column(String(150), unique = True, nullable=False)
	    address =  Column(String(564))
	    birthday = Column(Date)
	    personal_phone = Column(String(20))
	    personal_celphone = Column(String(20))
	    group_id = Column(Integer, ForeignKey('group.id'))
	    group = relationship("Group")	
	    
	    def __repr__(self):
                return self.name	


Define your Views (views.py)
----------------------------

Now we are going to define our view to *Group* table

::
  
        class GroupGeneralView(GeneralView):
    		datamodel = SQLAModel(Group, db.session)
    		related_views = [ContactGeneralView()]


I hope this was easy enough! Some questions may arrise...

Must have properties:

:datamodel: is the db abstraction layer. Initialize it with your model and sqlalchemy session

Optional properties:

:related_views: if you want a master/detail view on the show and edit.

There are many more properties you can override to customize your views. you can define descriptions for columns, validators for forms, and many more

Take a look at the :doc:`api`.


But where is ContactGeneralView ? (that was a reference has a related_views) 

Let's define it::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)

        label_columns = {'group':'Contacts Group'}
        list_columns = ['name','personal_celphone','birthday','group']

        show_fieldsets = [
            ('Summary',{'fields':['name','address','group']}),
            ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
            ]

Some explanation:

:label_columns: defines the labels for your columns. The framework will define the missing ones for you, with a pretty version of your column names.
:show_fieldsets: A fieldset (Django style).


Register (views.py)
-------------------

Register everything, to present the models and create the menu::

        genapp = BaseApp(app, db)
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


