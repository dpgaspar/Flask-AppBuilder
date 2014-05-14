Quick How to
============

On this chapter we will create a very simple contacts application you can find a
`Live Demo <http://flaskappbuilder.pythonanywhere.com/>`_ (login with guest/welcome).

And the source code for this chapter on
`examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto>`_

The Base Skeleton Application
-----------------------------

If your working with the base skeleton application (take a look at the :doc:`installation` chapter).

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

Let's create a very simple contacts application.
F.A.B uses the excellent SQLAlchemy ORM package,
you should be familiar with it's declarative syntax to define your database models on F.A.B.

On our example application we are going to define two tables,
a *Contact's* table that will hold the contacts detailed information,
and a *Group* table to group our contacts or classify them.
We could additionally define a *Gender* table, to serve the role of enumerated values for 'Male' and 'Female'.

Although your not obliged to, i advise you to inherit your model classes from *Base* and *BaseMixin*.
You can of course inherit from *db.Model* normal Flask-SQLAlchemy.
The reason for this is that *Base* is on the same declarative space of F.A.B.
and using it will allow you to define relations to User's.

You can add automatic *Audit* triggered columns to your models, by inherit them from *AuditMixin* also. (see :doc:`api`)

So, first we are going to create a *Group* table, to group our contacts

Define your models (models.py)
------------------------------

The *Group* table.

::

    from sqlalchemy import Column, Integer, String, ForeignKey, Date
    from sqlalchemy.orm import relationship
    from flask.ext.appbuilder.models.mixins import BaseMixin
    from flask.ext.appbuilder import Base

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

Now we are going to define our view for *Group* table.
This view will setup functionality for create, remove, update and show primitives for your model's definition.

Inherit from *GeneralView* class that inherits from *BaseCRUDView* that inherits from *BaseModelView*,
so you can override all their public properties to configure many details for your CRUD primitives.
take a look at **Advanced Configuration** on this page.

::

    class GroupGeneralView(GeneralView):
        datamodel = SQLAModel(Group)
        related_views = [ContactGeneralView]


I hope this was easy enough! Some questions may arise...

Must have properties:

:datamodel: is the db abstraction layer. Initialize it with your view's model.

Optional properties:

:related_views: if you want a master/detail view on the show and edit. F.A.B.
    will relate 1/N relations automatically, it will display a show or edit view with tab (or accordion) with a list related record. You can relate charts also.

This is the most basic configuration (with an added related view).

If you want to add a view associated with an alternative backend (you can have views from multiple backends)
you can define it like this

::

    class GroupGeneralView(GeneralView):
        datamodel = SQLAModel(Group, other_db.session)
        related_views = [ContactGeneralView]

You must pass this view to *add_view* method instantiated.

But where is ContactGeneralView ? (that was a reference in *related_views* list) 

Let's define it::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact)

        label_columns = {'group':'Contacts Group'}
        list_columns = ['name','personal_celphone','birthday','group']

        show_fieldsets = [
            ('Summary',{'fields':['name','address','group']}),
            ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
            ]

Some explanation:

:label_columns: defines the labels for your columns. The framework will define the missing ones for you, with a pretty version of your column names.
:show_fieldsets: A fieldset (Django style). This is allow you to customize the add, show and edit views independently.


Register (views.py)
-------------------

Register everything, to present the models and create the menu

::

        genapp = BaseApp(app, db)
        genapp.add_view(GroupGeneralView, "List Groups",icon = "fa-folder-open-o",category = "Contacts",
                        category_icon = "fa-envelope")
        genapp.add_view(ContactGeneralView, "List Contacts",icon = "fa-envelope",category = "Contacts")

Take a look at the :doc:`api` for add_view method.

.. note::
	The icons for the menu on this examples are from font-awesome, Checkout fontAwesome `Icons <http://fontawesome.io/icons/>`_ names. Font-Awesome is already included and you can use any icon you like on menus and actions
	
With this very few lines of code (and could be fewer), you now have a web application with detailed security for each CRUD primitives and Menu options, authentication, and form field validation. Yet you can extensively change many details, add your own triggers before or after CRUD primitives, develop your own web views and integrate them.


You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Live quickhowto `Demo <http://flaskappbuilder.pythonanywhere.com/>`_ (login with guest/welcome).

Some images:

.. image:: ./images/login_db.png
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
        datamodel = SQLAModel(Group)
        base_permissions = ['can_add','can_delete']
            
With this initial config, the framework will only create 'can_add' and 'can_delete'
permissions on GroupGeneralView as the only allowed. So users and even the administrator
of the application will not have the possibility to add list or show permissions on Group table view.
Base available permission are: can_add, can_edit, can_delete, can_list, can_show. More detailed info on :doc:`security`

    - **Base Filtering**
    
To filter a views data, just set the *base_filter* property with your base filters. These will allways be applied first on any search. 

It's very flexible, you can apply multiple filters with static values, or values based on a function you define. On this next example we are filtering a view by the logged in user and with column *name* starting with "a"

*base_filters* is a list of lists with 3 values [['column name',FilterClass,'filter value],...]

::

    def get_user():
        return g.user
        
    class MyView(GeneralView):
        datamodel = SQLAModel(MyTable)
        base_filters = [['created_by', FilterEqualFunction, get_user],
                        ['name', FilterStartsWith, 'a']]


- **Default Order**
    
Use a default order on your lists, this can be overridden by the user on the UI. Data structure ('col_name':'asc|desc')

::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyTable)
        base_order = ('my_col_to_be_ordered','asc')


- **Forms**

- You can create a custom query filter for all related columns like this::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact)
        add_form_query_rel_fields = [('group',
                    SQLAModel(Group, db.session),
                    [['name',FilterStartsWith,'W']]
                    )]


This will filter list combo on Contact's model related with Group model. The combo will be filtered with entries that start with W. You can define individual filters for add and edit. Take a look at the :doc:`api`
If you want to filter multiple related fields just add tuples to the list, remember you can add multiple filters for each field also, take a look at the *base_filter* property::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact)
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
        datamodel = SQLAModel(MyModel)
        add_form = AddFormWTF


- You can define what columns will be included on Add or Edit forms,
    for example if you have automatic fields like user or date, you can remove this from the Add Form::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyModel)
        add_columns = ['my_field1','my_field2']
        edit_columns = ['my_field1']

- You can contribute with any additional field that are not on a table/model,
    for example a confirmation field::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact)
        add_form_extra_fields = {'extra': TextField(gettext('Extra Field'),
                        description=gettext('Extra Field description'),
                        widget=BS3TextFieldWidget())}


- You can contribute with your own additional form validations rules.
    Remember the framework will automatically validate any field that is defined on the database
    with *Not Null* (Required) or Unique constraints::

    class MyView(GeneralView):
        datamodel = SQLAModel(MyModel)
        validators_columns = {'my_field1':[EqualTo('my_field2',
                                            message=gettext('fields must match'))
                                          ]
        }

Take a look at the :doc:`api`. Experiment with *add_form*, *edit_form*, *add_columns*, *edit_columns*, *validators_columns*, *add_form_extra_fields*, *edit_form_extra_fields*
