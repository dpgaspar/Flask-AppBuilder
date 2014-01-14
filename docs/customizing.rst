Customizing
===========

You can override and customize almost everything on the UI, or use different templates and widgets already on the framework.

Event better you can develop your own widgets or templates and contribute to the project.

Changing themes
---------------

F.A.B comes with bootwatch themes ready to use, to the bootstrap default theme just change the APP_THEME key

	- On config.py (from flask-appbuilder-skeleton), using spacelab theme::

        #APP_THEME = ""                  # default
        #APP_THEME = "cerulean.css"      # COOL
        #APP_THEME = "amelia.css"
        #APP_THEME = "cosmo.css"
        #APP_THEME = "cyborg.css"       # COOL
        #APP_THEME = "flatly.css"
        #APP_THEME = "journal.css"
        #APP_THEME = "readable.css"
        #APP_THEME = "simplex.css"
        #APP_THEME = "slate.css"          # COOL
        APP_THEME = "spacelab.css"      # NICE
        #APP_THEME = "united.css"
        #APP_THEME = "yeti.css"
    

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

What happened here? We should allways extend from "appbuilder/base.html" this is the base template that will include all CSS's, Javascripts, and contruct the menu based on the user's security definition.

Next we will override the "content" block, we could override other areas like CSS, extend CSS, Javascript or extend javascript. We can even override the base.html completely

I've presented the text on the content like::

    {{_("text to be translated")}}

So that we can use Babel to translate our index text

2 - Define an IndexView

Define a special and simple view inherite from IndexView::

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
		

Changing Widgets amd Templates
------------------------------

F.A.B. has a collection of widgets to change your views presentation, you can create your own and override, or (even better) create them and contribute to the project on git.

All views have templates that will display widgets in a certain layout. For example you can display a record related lists on tab (default) or on the same page.

::

    class ServerDiskTypeGeneralView(GeneralView):
        datamodel = SQLAModel(ServerDiskType, db.session)
        list_columns = ['quantity', 'disktype']


    class ServerGeneralView(GeneralView):
        datamodel = SQLAModel(Server, db.session)
        related_views = [ServerDiskTypeGeneralView()]

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
        related_views = [ServerDiskTypeGeneralView()]

        show_template = 'appbuilder/general/model/show_cascade.html'
        edit_template = 'appbuilder/general/model/edit_cascade.html'

        list_columns = ['name', 'serial']
        order_columns = ['name', 'serial']
        search_columns = ['name', 'serial']


.. image:: ./images/list_cascade_block.png
    :width: 100%


on version 0.3.10 you have the following widgets already available

- ListWidget (default)
- ListItem
- ListThumbnail
- ListBlock

If you want to develop your own widgets just look at the code on:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/flask_appbuilder/templates/appbuilder/general/widgets

Implement your own and then create a very simple class like this one::

    class MyWidgetList(ListWidget):
        template = '/widgets/my_widget_list.html'
        
