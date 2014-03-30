Customizing
===========

You can override and customize almost everything on the UI, or use different templates and widgets already on the framework.

Even better you can develop your own widgets or templates and contribute to the project.

Changing themes
---------------

F.A.B comes with bootswatch themes ready to use, to change bootstrap default theme just change the APP_THEME key's value.

- On config.py (from flask-appbuilder-skeleton), using spacelab theme::

    APP_THEME = "spacelab.css"

- Not using a config.py on your applications, set the key like this::

	app.config['APP_THEME'] = "spacelab.css"
 
You can choose from the folowing `themes <https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/blob/master/config.py>`_  


Changing the index
------------------

The index can be easily overridden by your own. You must develop your template, then define it in a IndexView and pass it to BaseApp

The default index template is very simple, you can create your own like this:

1 - Develop your template (on your <PROJECT_NAME>/app/templates/my_index.html)::

    {% extends "appbuilder/base.html" %}
    {% block content %}
    <div class="jumbotron">
      <div class="container">
        <h1>{{_("My App on F.A.B.")}}</h1>
        <p>{{_("My first app using F.A.B, bla, bla, bla")}}</p>
      </div>
    </div>
    {% endblock %}

What happened here? We should always extend from "appbuilder/base.html" this is the base template that will include all CSS's, Javascripts, and contruct the menu based on the user's security definition.

Next we will override the "content" block, we could override other areas like CSS, extend CSS, Javascript or extend javascript. We can even override the base.html completely

I've presented the text on the content like::

    {{_("text to be translated")}}

So that we can use Babel to translate our index text

2 - Define an IndexView

Define a special and simple view inherit from IndexView::

    class MyIndexView(IndexView):
        index_template = 'index.html'

3 - Tell F.A.B to use your index view::

    baseapp = BaseApp(app, db, indexview = MyIndexView)

Changing Menu Construction
--------------------------

You can change the way the menu is constructed adding your own links, separators and changing the navbar reverse property.

By default menu is constructed based on your classes and in a reversed navbar. Let's take a quick look on how to easily change this

	- Change the reversed navbar style, on baseapp initialization::
	
		baseapp = BaseApp(app, db, menu=Menu(reverse=False))
		
	- Add your own menu links, on a default reversed navbar::
	
		baseapp = BaseApp(app, db)
		# Register a view, rendering a top menu without icon
		baseapp.add_view(MyGeneralView, "My View")
		# Register a view, a submenu "Other View" from "Other" with a phone icon
		baseapp.add_view(MyOtherGeneralView, "Other View", icon='fa-phone', category="Others")
		# Add a link
		baseapp.add_link("google", href="www.google.com", icon = "fa-google-plus")
		
	- Add separators::
	
		baseapp = BaseApp(app, db)
		# Register a view, rendering a top menu without icon
		baseapp.add_view(MyGeneralView1, "My View 1", category="My Views")
		baseapp.add_view(MyGeneralView2, "My View 2", category="My Views")
		baseapp.add_separator("My Views")
		baseapp.add_view(MyGeneralView3, "My View 3", category="My Views")
		

Changing Widgets and Templates
------------------------------

F.A.B. has a collection of widgets to change your views presentation, you can create your own and override, or (even better) create them and contribute to the project on git.

All views have templates that will display widgets in a certain layout. For example you can display a record related lists on tab (default) or on the same page.

::

    class ServerDiskTypeGeneralView(GeneralView):
        datamodel = SQLAModel(ServerDiskType, db.session)
        list_columns = ['quantity', 'disktype']


    class ServerGeneralView(GeneralView):
        datamodel = SQLAModel(Server, db.session)
        related_views = [ServerDiskTypeGeneralView]

        show_template = 'appbuilder/general/model/show_cascade.html'
        edit_template = 'appbuilder/general/model/edit_cascade.html'

        list_columns = ['name', 'serial']
        order_columns = ['name', 'serial']
        search_columns = ['name', 'serial']
        
        
The above example will override the show and edit templates that will change the related lists layout presentation.

.. image:: ./images/list_cascade.png
    :width: 100%


If you want to change the above example, and change the way the server disks are displayed has a list just use the available widgets::

    class ServerDiskTypeGeneralView(GeneralView):
        datamodel = SQLAModel(ServerDiskType, db.session)
        list_columns = ['quantity', 'disktype']
        list_widget = ListBlock

    class ServerGeneralView(GeneralView):
        datamodel = SQLAModel(Server, db.session)
        related_views = [ServerDiskTypeGeneralView]

        show_template = 'appbuilder/general/model/show_cascade.html'
        edit_template = 'appbuilder/general/model/edit_cascade.html'

        list_columns = ['name', 'serial']
        order_columns = ['name', 'serial']
        search_columns = ['name', 'serial']


.. image:: ./images/list_cascade_block.png
    :width: 100%


You have the following widgets already available

- ListWidget (default)
- ListItem
- ListThumbnail
- ListBlock

If you want to develop your own widgets just look at the code on:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/flask_appbuilder/templates/appbuilder/general/widgets

Implement your own and then create a very simple class like this one::

    class MyWidgetList(ListWidget):
        template = '/widgets/my_widget_list.html'
        

Change Default View Behaviour
-----------------------------

If you want to have Add, edit and list on the same page, this can be done. This could be very helpful on master/detail lists (inline) on views based on tables with very few columns.

All you have to do is to mix *CompactCRUDMixin* class with the *GeneralView* class.

::

    from flask.ext.appbuilder.baseapp import BaseApp
    from flask.ext.appbuilder.models.datamodel import SQLAModel
    from flask.ext.appbuilder.views import GeneralView, CompactCRUDMixin
    from app.models import Project, ProjectFiles
    from app import app, db


    class MyInlineView(CompactCRUDMixin, GeneralView):
        datamodel = SQLAModel(MyInlineTable, db.session)

    class MyView(GeneralView):
        datamodel = SQLAModel(MyViewTable, db.session)
        related_views = [MyInlineView]

    baseapp = BaseApp(app, db)
    baseapp.add_view(MyView(), "List My View",icon = "fa-table",category = "My Views")
    baseapp.add_view_no_menu(MyInlineView())


Notice the class mixin, with this configuration you will have a *Master View* with the inline view *MyInlineView* where you can Add and Edit on the same page.

Of course you could use the mixin on *MyView* also, use it only on GeneralView classes.

Take a look at the example: https://github.com/dpgaspar/Flask-appBuilder/tree/master/examples/quickfiles


.. image:: ./images/list_compact_inline.png
    :width: 100%

Next we will take a look at a different view behaviour. A master detail style view, master is a view associated with a database table that is linked to the detail view.

Let's assume our quick how to example, a simple contacts applications. We have *Contact* table related with *Group* table.

So we are using master detail view, first we will define the detail view (this view can be customized like the examples above)::

    class ContactGeneralView(GeneralView):
        datamodel = SQLAModel(Contact, db.session)


Then we define the master detail view, where master is the one side of the 1-N relation::

    class GroupMasterView(MasterDetailView):
        datamodel = SQLAModel(Group, db.session)
        related_views = [ContactGeneralView]


Finally and register everything::

    genapp = BaseApp(app, db)
    genapp.add_view(GroupMasterView(), "List Groups", icon="fa-folder-open-o", category="Contacts")
    genapp.add_separator("Contacts")
    genapp.add_view(ContactGeneralView(), "List Contacts", icon="fa-envelope", category="Contacts")


.. image:: ./images/list_master_detail.png
    :width: 100%

