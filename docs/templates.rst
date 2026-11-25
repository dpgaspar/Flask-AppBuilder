Templates
=========

F.A.B. uses jinja2, all the framework templates can be overridden entirely or partially.
This way you can add your own html on jinja2 templates.
This can be done before or after defined blocks on the page,
without the need of developing a template from scratch because you just want to add small changes on it.
Next is a quick description on how you can do this

CSS and Javascript
------------------

To add your own CSS's or javascript application wide.
You will need to tell the framework to use your own base *jinja2* template, this
template is extended by all the templates. It's very simple: first create your own
template in your **templates** directory.

On a simple application structure create *mybase.html* (or whatever name you want)::

    <my_project>
        <app>
            __init__.py
            models.py
            views.py
            <templates>
                **mybase.html**


Then on mybase.html add your js files and css files, use **head_css** for css's and **head_js** for javascript.
These are *jinja2* blocks, F.A.B. uses them so that you can override or extend critical parts of the default
templates, making it easy to change the UI, without having to develop your own from scratch::

    {% extends 'appbuilder/baselayout.html' %}

    {% block head_css %}
        {{ super() }}
        <link rel="stylesheet" href="{{url_for('static',filename='css/your_css_file.css')}}"></link>
    {% endblock %}

    {% block head_js %}
        {{ super() }}
        <script src="{{url_for('static',filename='js/your_js_file.js')}}"></script>
    {% endblock %}


If you want to import your javascript files at the end of the templates use **tail_js**::

    {% block tail_js %}
        {{ super() }}
        <script src="{{url_for('static',filename='js/your_js_file.js')}}"></script>
    {% endblock %}


Finally tell the framework to use it, instead of the default base template,
when initializing on __init__.py use the *base_template* parameter::

    appbuilder = AppBuilder(app, db.session, base_template='mybase.html')

You have an example that changes the way the menu is displayed on
`examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quicktemplates>`_

This main structure of jinja2 on the baselayout template is::

        {% block head_meta %}
            ... HTML Meta
        {% endblock %}
        {% block head_css %}
            ... CSS imports (bootstrap, fontAwesome, select2, fab specific etc...
        {% endblock %}
        {% block head_js %}
            ... JS imports (JQuery, fab specific)
        {% endblock %}
        {% block body %}
            {% block navbar %}
                ... The navigation bar (Menu)
            {% endblock %}
             {% block messages %}
                ... Where the flask flash messages are shown ("Added row", etc)
              {% endblock %}
              {% block content %}
                ... All the content goes here, forms, lists, index, charts etc..
              {% endblock %}
            {% block footer %}
                ... The footer, by default its almost empty.
            {% endblock %}
        {% block tail_js %}
        {% endblock %}

Navigation Bar
--------------

There is also the possibility to customize the navigation bar. 
You can completely override it, or just partially.

To completely override the navigation bar, implement your own base layout as described earlier
and then extend the existing one and override the **navbar** block.

As an example, let's say you created your own base layout named **my_layout.html** 
in your **templates** folder::

    {% extends 'appbuilder/baselayout.html' %}

    {% block navbar %}
        <div class="navbar" role="navigation">
           <div class="container">
                <div class="navbar-header">
                        ....
                </div>
                <div class="navbar-collapse collapse">
                        ....
                </div>
           </div>
        </div>
    {% endblock %}

Remember to tell Flask-Appbuilder to use your layout instead (previous chapter).

The best way to just override the navbar partially is to override the existing templates
from the framework. You can always do this with any template. There are two good candidates for this:

:/templates/appbuilder/navbar_menu.html: This will render the navbar menus.
:/templates/appbuilder/navbar_right.html: This will render the right part of the navigation bar (locale and user).

List Templates
--------------

Using the contacts app example, we are going to see how to override or insert jinja2 on specific sections
of F.A.B. list template. Remember that the framework uses templates with generated widgets, this widgets are big
widgets, because they render entire sections of a page.
On list's of records you will have two widgets: the search widget and the list widget. You will have
a template with the following sections, where you can add your template sections over, before and after
each block:

- List template
    - Block "content"
        - Block "list_search"
            - Search Widget
        - End Block "list_search"
        - Block "list_list"
            - List Widget
        - End Block "list_list"
    - End Block "content"

To insert your template section over a block, say "list_search" just do:

::

    {% extends "appbuilder/general/model/list.html" %}

        {% block list_search scoped %}
            This Text will replace the search widget
        {% endblock %}

To insert your template section after a block do:

::

    {% extends "appbuilder/general/model/list.html" %}

        {% block list_search scoped %}
            {{ super() }}
            This Text will show after the search widget
        {% endblock %}

I guess you get the general ideal, make use of {{ super() }} to render the block's original content.
To use your templates override **list_template** to your templates relative path, on your ModelView's declaration.

If you have your template on ./your_project/app/templates/list_contacts.html

::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        list_template = 'list_contacts.html'


In your template you can do something like this

::

    {% extends "appbuilder/general/model/list.html" %}

    {% block content %}
        Text on top of the page
        {{ super() }}
        {% block list_search scoped %}
            Text before the search section
            {{ super() }}
        {% endblock %}

        {% block list_list scoped %}
            Text before the list
            {{ super() }}
        {% endblock %}
    {% endblock %}

Add Templates
--------------

In this section we will see how to override the add template form.
You will have only one widget, the add form widget. So you will have
a template with the following sections, where you can add your template sections over, before and after
each block:

- Add template
    - Block "content"
        - Block "add_form"
            - Add Widget
        - End Block "add_form"
    - End Block "content"

To insert your template section before a block, say "add_form" just create your own template like this:

::

    {% extends "appbuilder/general/model/add.html" %}

        {% block add_form %}
            This Text is before the add form widget
            {{ super() }}
        {% endblock %}

To use your template define you ModelView with **add_template** declaration to your templates relative path

If you have your template in ./your_project/app/templates/add_contacts.html

::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)

        add_template = 'add_contacts.html'

Edit Templates
--------------

In this section we will see how to override the edit template form.
You will have only one widget the edit form widget, so you will have
a template with the following sections, where you can add your template sections over, before and after
each block:

- Add template
    - Block "content"
        - Block "edit_form"
            - Edit Widget
        - End Block "edit_form"
    - End Block "content"

To insert your template section before the edit widget, just create your own template like this:

::

    {% extends "appbuilder/general/model/edit.html" %}

        {% block edit_form %}
            This Text is before the edit form widget
            {{ super() }}
        {% endblock %}

To use your template define you ModelView with **edit_template** declaration to your templates relative path

If you have your template in ./your_project/app/templates/edit_contacts.html

::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)

        edit_template = 'edit_contacts.html'


Show Templates
--------------

In this section we will see how to override the show template.
You will have only one widget the show widget, so you will have
a template with the following sections, where you can add your template sections over, before and after
each block:

- Show template
    - Block "content"
        - Block "show_form"
            - Show Widget
        - End Block "show_form"
    - End Block "content"

To insert your template section before a block, say "show_form" just create your own template like this:

::

    {% extends "appbuilder/general/model/show.html" %}

        {% block show_form %}
            This Text is before the show widget
            {{ super() }}
        {% endblock %}

To use your template define you ModelView with **show_template** declaration to your templates relative path

If you have your template in ./your_project/app/templates/show_contacts.html

::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)

        show_template = 'show_contacts.html'


Edit/Show Cascade Templates
---------------------------

In cascade templates for related views the above rules apply, but you can use an extra block
to insert your template code before, after or over the related view list widget.
For show cascade templates you have the following structure:

- Show template
    - Block "content"
        - Block "show_form"
            - Show Widget
        - End Block "show_form"
        - Block "related_views"
            - Related Views Widgets
        - End Block "related_views"
    - End Block "content"

Widgets
-------

Widgets are reusable, you can and should implement your own. Widgets are a special kind of jinja2
templates. They will be contained inside a python class, and rendered on a jinja2 template. So
**list_template**, **add_template**, **edit_template**, **show_template** will work like layouts
with widgets.

To create your own widgets follow the next recipe.

Example 1: Custom list widget
`````````````````````````````

- Make your own widget template, we are going to create a very simple list widget.
  since version 1.4.1 list widgets extend **base_list.html** this will make your life
  simpler, this base template declares the following blocks you should use, when implementing
  your own widget for lists::
    
    {% block list_header scoped %}
        This is where the list controls are rendered, extend it to *inject* your own controls.
    {% endblock %}

    {% block begin_content scoped %}
        Area next to the controls
    {% endblock %}

    {% block begin_loop_header scoped %}
        Nice place to render your list headers.
    {% endblock %}

    {% block begin_loop_values %}
        Make your loop and render the list itself.
    {% endblock %}

Let's make a simple example::

    {% import 'appbuilder/general/lib.html' as lib %}
    {% extends 'appbuilder/general/widgets/base_list.html' %}

    {% block list_header %}
       {{ super() }}
       <a href="url_for('Class.method for my control')" class="btn btn-sm btn-primary"
            <i class="fa fa-rocket"></i>
       </a>
    {% endblock %}

    {% block begin_loop_values %}
        {% for item in value_columns %}
            {% set pk = pks[loop.index-1] %}
            {% if actions %}
                <input id="{{pk}}" class="action_check" name="rowid" value="{{pk}}" type="checkbox">
            {% endif %}
            {% if can_show or can_edit or can_delete %}
                {{ lib.btn_crud(can_show, can_edit, can_delete, pk, modelview_name, filters) }}
            {% endif %}
            </div>
        
            {% for value in include_columns %}
                <p {{ item[value]|safe }}</p>
            {% endfor %}
        {% endfor %}
    {% endblock %}


This example will just use two blocks **list_header** and **begin_loop_values**.
On **list_header** we are rendering an extra button/link to a class method.
Notice that first we call **super()** so that our control will be placed next to
pagination, add button and back button 

.. note:: If you just want to add a new control next to the list controls and keep everything else
   from the predefined widget. extend your widget from {% extends 'appbuilder/general/widgets/list.html' %}
   and just implement **list_header** the way it's done in this example.

Next we will render the values of the list, so we will override the **begin_loop_values**
block. Widgets have the following jinja2 vars that you should use:

- can_show: Boolean, if the user has access to the show view.
- can_edit: Boolean, if the user has access to the edit view.
- can_add: Boolean, if the user has access to the add view.
- can_delete: Boolean, if the user has access to delete records.
- value_columns: A list of Dicts with column names as keys and record values as values.
- include_columns: A list with columns to include in the list, and their order.
- order_columns: A list with the columns that can be ordered.
- pks: A list of primary key values.
- actions: A list of declared actions.
- modelview_name: The name of the ModelView class responsible for controlling this template.

Save your widget template in your templates folder. I advise you to create a 
subfolder named *widgets*. So in our example we will keep our template in
*/templates/widgets/my_list.html*.

- Next we must create our python class to contain our widget. In your **app** folder
  create a file named widgets.py::

    from flask_appbuilder.widgets import ListWidget
    
    
    class MyListWidget(ListWidget):
         template = 'widgets/my_list.html'


- Finally use your new widget on your views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)
        list_widget = MyListWidget

Example 2: Custom show widget
`````````````````````````````

By default, :doc:`actions` related buttons are located at the end of the detail
page. If you now have a longer detail page, it can be cumbersome for your users
to have to go to the bottom of the page to perform the actions. Let's just add
a second set of buttons to the top of the page.

To do this, do the following (similar to the steps above):

- Create a template override file *<module>/templates/widgets/my_show.html*::

    {% extends "appbuilder/general/widgets/show.html" %}
    {% block columns %}
        <div class="well well-sm">
            {{ lib.render_action_links(actions, pk, modelview_name) }}
            {{ lib.lnk_back() }}
        </div>
        {{ super() }}
    {% endblock %}

  Please note that we have just overridden the jinja block named ``columns``,
  prepended our own HTML code and then called the original block (using ``super()``).

- Create the custom ShowWidget class::

    from flask_appbuilder.widgets import ShowWidget
   
    class MyShowWidget(ShowWidget):
        template = 'widgets/show.html'

- And finally refer to your widget in your view:

    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)
        show_widget = MyShowWidget


Other widget types
``````````````````

Flask-AppBuilder has already some widgets that you can choose from, try them out:

- ListWidget - The default for lists.
- ListLinkWidget - The default for lists.
- ListThumbnail - For lists, nice to use with photos.
- ListItem - Very simple list of items.
- ListBlock - For lists, similar to thumbnail.
- FormWidget - For add and edit.
- FormHorizontalWidget - For add and edit.
- FormInlineWidget - For add and edit
- ShowWidget - For show view.
- ShowBlockWidget - For show view.
- ShowVerticalWidget - For show view.

Take a look at the `widgets <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/widgets>`_ example.

Library Functions
-----------------

F.A.B. has the following library functions that you can use to render bootstrap 3
components easily. Using them will ease your productivity and help you introduce
new html that shares the same look and feel of the framework.

- Panel component::

    {{ lib.panel_begin("Panel's Title") }}
        Your html goes here
    {{ lib.panel_end() }}

- Accordion (pass your view's name, or something that will serve as an id)::

    {% call lib.accordion_tag(view.__class__.__name__,"Accordion Title", False) %}
        Your HTML goes here
    {% endcall %}

