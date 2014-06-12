Base Views
==========

Views are the base concept of F.A.B.
they work like a class that represent a concept and present the views and methods to implement it.

Each view is a Flask blueprint that will be created for you automatically by the framework.
This is a simple but powerful concept.
You will map your methods to routing points, and each method will be registered
as a possible security permission if you want to.

So your methods will have automatic routing points much like Flask, but this time in a class.
Additionally you can have granular security (method access security) that can be associated with a user's role
(take a look at :doc:`security` for more detail).

The views documented on this chapter are the building blocks of F.A.B, but the juicy part is on the next chapter
with ModelView, ChartView and others.

BaseView
--------

All views inherit from this class.
it's constructor will register your exposed urls on flask as a Blueprint,
as well as all security permissions that need to be defined and protected.

You can use use this kind of view to implement your own custom pages,
attached to a menu or linked from any point of your site.

Decorate your url routing methods with **@expose**.
additionally add **@has_access** decorator to tell flask that this is a security protected method.

Using the Flask-AppBuilder-Skeleton (take a look at the :doc:`installation` chapter). Edit views.py file and add::

    from flask.ext.appbuilder import AppBuilder, expose, BaseView
    from app import appbuilder

    class MyView(BaseView):
        route_base = "/myview"

        @expose('/method1/<string:param1>')
        def method1(self, param1):
            # do something with param1
            # and return it
            return param1

        @expose('/method2/<string:param1>')
        def method2(self, param1):
            # do something with param1
            # and render it
            param1 = 'Hello %s' % (param1)
            return param1

    appbuilder.add_view_no_menu(MyView())
    

You can find this example on:

 https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/simpleview1

look at the file app/views.py

This simple example will register your view with two routing urls on:

    - /myview/method1/<string:param1>
    - /myview/method2/<string:param1>
    
No menu will be created for this, no security permissions will be created also, if you want to enable detailed security access for your methods just add @has_access decorator to them.

Now run this example
::

    $ python run.py

You can test your methods using the following url's:

http://localhost:8080/myview/method1/john

http://localhost:8080/myview/method2/john

Has you can see this methods are public, let's change this example, edit views.py and change it to::

    from flask.ext.appbuilder import AppBuilder, BaseView, expose, has_access
    from app import appbuilder


    class MyView(BaseView):

        default_view = 'method1'

        @expose('/method1/')
        @has_access
        def method1(self):
            # do something with param1
            # and return to previous page or index
            return 'Hello'

        @expose('/method2/<string:param1>')
        @has_access
        def method2(self, param1):
            # do something with param1
            # and render template with param
            param1 = 'Goodbye %s' % (param1)
            return param1

    appbuilder.add_view(MyView, "Method1", category='My View')
    appbuilder.add_link("Method2", href='/myview/method2/jonh', category='My View')


You can find this example on https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/simpleview2

.. automodule:: flask.ext.appbuilder.baseviews

    .. autofunction:: expose

.. automodule:: flask.ext.appbuilder.security.decorators

    .. autofunction:: has_access


This will create the following menu

.. image:: ./images/simpleview2.png
    :width: 100%

Notice that these methods will render simple pages not integrated with F.A.B's look and feel.
It's easy to render your method's response integrated with the app's look and feel,
for this you have to create your own template.
under your projects directory and app folder create a folder named 'templates'
inside it create a file name 'method3.html'

1 - Develop your template (on your <PROJECT_NAME>/app/templates/method3.html)::

    {% extends "appbuilder/base.html" %}
    {% block content %}
        <h1>{{param1}}</h1>
    {% endblock %}

2 - Add the following method on your *MyView* class::

    @expose('/method3/<string:param1>')
    @has_access
    def method3(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Goodbye %s' % (param1)
        return render_template('method3.html',
                               param1 = param1,
                               appbuilder=self.appbuilder)

3 - Create a menu link to your new method::

    appbuilder.add_link("Method3", href='/myview/method3/jonh', category='My View')

Has you can see you just have to extend "appbuilder/base.html" on your template and then override *block content*.
You have many other *blocks* to override extending css includes, javascript, headers, tails etc...
Next use **Flask** **render_template** to render you new template


SimpleFormView
--------------

Inherit from this view to provide base processing for your customized form views.

In principle you will only need this kind of view to present forms that are not Database Model based,
because when they do F.A.B. can automatically generate them and you can add or remove fields,
as well as custom validators. For this you can use ModelView instead.

To create a custom form view, first define your WTF form fields, but inherit them from F.A.B. *DynamicForm*.

::

    from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField, PasswordField
    from flask.ext.appbuilder.forms import DynamicForm

    class MyForm(DynamicForm):
        field1 = TextField(('Field1'),
            description=('Your field number one!'),
            validators = [Required()])
        field2 = TextField(('Field2'),
            description=('Your field number two!'))


Now define your form view to expose urls, create a menu entry, create security accesses, define pre and post processing.

Implement *form_get* and *form_post* to implement your form pre-processing and post-processing

::

    from flask_appbuilder.views import SimpleFormView
    from flask.ext.babelpkg import lazy_gettext as _


    class MyFormView(SimpleFormView):
        route_base = '/myform'

        form = MyForm
        redirect_url = '/myform'
        form_title = 'This is my first form view'

        message = 'My form submitted'

        def form_post(self, form):
            # process form
            flash(as_unicode(self.message), 'info')

    appbuilder.add_view(MyFormView, "My form View", href="/myform", icon="fa-group", label=_('My form View'),
                         category="My Forms", category_icon="fa-cogs")


Notice that this class derives from *BaseView* so all properties from the parent class can be overridden also.
Notice also how label uses babel's lazy_gettext as _('text') function so that your menu items can be translated.

Most important Base Properties:

:form_title: The title to be presented (this is mandatory)
:form_columns: The form column names to include
:form: Your form class (WTFORM) (this is mandatory) 
    

