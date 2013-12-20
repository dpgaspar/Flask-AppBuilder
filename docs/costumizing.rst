Costumizing
===========

You can override and costumize almost everything on the UI, or use diferent templates and widgets already on the framework.

Event better you can develop your own widgets or templates and contribute to the project.


Changing the index
------------------

The index can be easely override by your own. You must develop your template, then define it in a IndexView and pass it to BaseApp

The default index template is very simple, you can create your own like this:

1 - Develop your template (own your <PROJECT_NAME>/app/templates/my_index.html)::

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

    class MyIndexView(BaseView):
        index_template = 'index.html'

3 - Tell F.A.B to use your index view::

    baseapp = BaseApp(app, db, indexview = MyIndexView)

