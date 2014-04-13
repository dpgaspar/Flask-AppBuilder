Quick How to
============

The Base Skeleton Application
-----------------------------

If your working with the base skeleton application :doc:`installation`

you now have the following directory structure::

    <your project name>/
        config.py : All the application's configuration
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
	Since version 0.3.9 i advise not using Flask-SqlAlchemy to define your tables, because you will be in a different declarative model from the security tables of AppBuilder.
	If you want to use AuditMixin :doc:`api` or include a relation to a User or login User, you must be on the same declarative base.
	Use BaseMixin to have automatic table name baptism like in Flask-SqlAlchemy, and inherit also from Base, import::

		flask.ext.appbuilder import Base
	
	This "Base" is the same declarative model of F.A.B.

Define your models (models.py)
------------------------------

The *Group* table.

::

    class Group(BaseMixin, Base):
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique = True, nullable=False)

        def __repr__(self):
            return self.name

The *Contacts* table.

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

Now we are going to define our view for *Group* table

::

    class GroupGeneralView(GeneralView):
        datamodel = SQLAModel(Group, db.session)
        related_views = [ContactGeneralView]


I hope this was easy enough! Some questions may arise...

Must have properties:

:datamodel: is the db abstraction layer. Initialize it with your model and sqlalchemy session

Optional properties:

:related_views: if you want a master/detail view on the show and edit. F.A.B. will relate 1/N relations automatically, it will display a show or edit view with tab (or accordion) with a list related record. You can relate charts also.

There are many more properties you can override to customize your views. you can define descriptions for columns, your own validators for form fields, base filters etc

Take a look at the :doc:`api`.


But where is ContactGeneralView ? (that was a reference in *related_views* list) 

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

Register everything, to present the models and create the menu

::

        genapp = BaseApp(app, db)
        genapp.add_view(GroupGeneralView(), "List Groups",icon = ""fa-folder-open-o"",category = "Contacts")
        genapp.add_view(ContactGeneralView(), "List Contacts",icon = "fa-envelope",category = "Contacts")

Take a look at the :doc:`api` for add_view method.

.. note::
	The icons for the menu on this examples are from font-awesome, take a look at the `icons <http://fontawesome.io/icons/>`_ names. Font-Awesome is already included and you can use any icon you like on menus and actions
	

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Live quickhowto `Demo <http://flaskappbuilder.pythonanywhere.com/>`_ (login with guest/welcome).

Some images:

.. image:: ./images/login.png
    :width: 100%

.. image:: ./images/group_list.png
    :width: 100%

.. image:: ./images/contact_list.png
    :width: 100%

Advanced Configuration
----------------------

    - **Security**

To block or set the allowed permissions on a view, just set the *base_permissions* property with the base permissions

::

    class GroupGeneralView(GeneralView):
        datamodel = SQLAModel(Group, db.session)
        base_permissions = ['can_add','can_delete']
            
With this initial config, the framework will only create 'can_add' and 'can_edit' permissions on GroupGeneralView as the only allowed. So users and even administrator of the application will not have the possibility to add delete permission on Group table view.

    - **Base Filtering**
    
To filter a views data, just set the *base_filter* property with your base filters. These will allways be applied first on any search. 

It's very flexible, you can apply multiple filters with static values, or values based on a function you define. On this next example we are filtering a view by the logged in user and with column *name* starting with "a"

*base_filters* is a list of lists with 3 values [['column name',FilterClass,'filter value],...]

::

    def get_user():
        return g.user
        
    class MyView(GeneralView):
        datamodel = SQLAModel(MyTable, db.session)
        base_filters = [['created_by', FilterEqualFunction, get_user],
                        ['name', FilterStartsWith, 'a']]


- **Default Order**
    
Use a default order on your lists, this can be overridden by the user on the UI. Data structure ('col_name':'asc|desc')

::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyTable, db.session)
        base_order = ('my_col_to_be_ordered','asc')


- **Forms**

- You can create a custom query filter for all related columns like this::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)
        add_form_query_rel_fields = [('group',
                    SQLAModel(Group, db.session),
                    [['name',FilterStartsWith,'W']]
                    )]


This will filter list combo on Contact's model related with Group model. The combo will be filtered with entries that start with W. You can define individual filters for add and edit. Take a look at the :doc:`api`
If you want to filter multiple related fields just add tuples to the list, remember you can add multiple filters for each field also, take a look at the *base_filter* property::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)
        add_form_query_rel_fields = [('group',
                    SQLAModel(Group, db.session),
                    [['name',FilterStartsWith,'W']]
                    ),
                    ('gender',
                    SQLAModel(Gender, db.session),
                    [['name',FilterStartsWith,'M']]
                    )
        ]


- You can define your own Add, Edit forms to override the automatic form creation::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyModel, db.session)
        add_form = AddFormWTF


- You can define what columns will be included on Add or Edit forms, for example if you have automatic fields like user or date, you can remove this from the Add Form::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyModel, db.session)
        add_columns = ['my_field1','my_field2']
        edit_columns = ['my_field1']

- You can contribute with any additional field that are not on a table/model, for example a confirmation field::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)
        add_form_extra_fields = {'extra': TextField(gettext('Extra Field'),
                        description=gettext('Extra Field description'),
                        widget=BS3TextFieldWidget())}


- You can contribute with your own additional form validations rules. Remember the framework will automatically validate any field that is defined on the database with *Not Null* (Required) or Unique constraints::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyModel, db.session)
        validators_columns = {'my_field1':[EqualTo('my_field2',
                                            message=gettext('fields must match'))
                                          ]
        }

Take a look at the :doc:`api`. Experiment with *add_form*, *edit_form*, *add_columns*, *edit_columns*, *validators_columns*, *add_form_extra_fields*, *edit_form_extra_fields*
