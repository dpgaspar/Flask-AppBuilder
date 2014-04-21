Views
=====

Views are the base concept of F.A.B. they works like a class that represent a concept and present the views and methods to implement it.

Each view is a Flask blueprint that will be created for you automatically by the framework. This is a simple but powerfull concept. You will map your methods to routing points, and each method will be registered as a possible security permission if you want to.

BaseView
--------

All views inherit from this class. it's constructor will register your exposed urls on flask as a Blueprint, as well as all security permissions that need to be defined and protected.

Generally you will not implement your views deriving from this class, unless your implementing a new base appbuilder view with your own custom methods.

Decorate your url routing methods with @expose. additionally add @has_access decorator to tell flask that this is a security protected method.

::

    from flask import render_template, redirect
    from flask.ext.appbuilder.baseviews import BaseView
    from flask.ext.appbuilder.baseviews import expose

    class MyView(BaseView):
        route_base = "/myview"

        index_template = "method2.html"

        @expose('/method1/<string:param1>')
        def method1(self, param1):
            # do something with param1
            # and return to previous page or index
            return redirect(self._get_redirect())

        @expose('/method2/<string:param1>')
        def method2(self, param1):
            # do something with param1
            # and render template with param
            return render_template(self.index_template, param1=param1, baseapp=self.baseapp)

    genapp = BaseApp(app, db)
    genapp.add_view_no_menu(ConfigView())
    

This simple example will register your view with two routing urls on:

    - /myview/method1/<string:param1>
    - /myview/method2/<string:param1>
    
No menu will be created for this, no security permissions will be created also, if you want to enable detailed security access for your methods just add @has_access decorator to them.
    
SimpleFormView
--------------

Inherit from this view to provide base processing for your customized form views. To create a custom form view, first define your WTF form fields, but inherit them from F.A.B. *DynamicForm*.

::

    from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField, PasswordField
    from flask.ext.appbuilder.forms import DynamicForm

    class MyForm(DynamicForm):
        field1 = TextField('Field1'),
            description=('Your field number one!'),
            validators = [Required()])
        field2 = TextField('Field2'),
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

    baseapp.add_view(MyFormView, "My form View", href="/myform", icon="fa-group", label=_('My form View'),
                         category="My Forms", category_icon="fa-cogs")


Notice that this class derives from *BaseView* so all properties from the parent class can be overridden also.
Notice also how label uses babel's lazy_gettext as _('text') function so that your menu item can be translated.

Most important Base Properties:

:form_title: The title to be presented (this is mandatory)
:form_columns: The form column names to include
:form: Your form class (WTFORM) (this is mandatory) 
    

