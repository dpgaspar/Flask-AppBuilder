Views
=====

Views are the base concept of F.A.B. they works like a class that represent a concept and present the views and methods to implement it.

Each view is a Flask blueprint that will be created for you automatically by the framework, in a simple but powerfull concept. You will map your method to routing points, and each method will be registered as a possible security permission if you want to.

BaseView
--------

All views derive from this class. it's constructor will register your exposed urls on flask as a Blueprint.

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
    

This simple example will register your view with two routing urls on, no menu will be created for this:

    - /myview/method1/<string:param1>
    - /myview/method2/<string:param1>
    
    
SimpleFormView
--------------

Derive from this view to provide some base processing for your costumized form views.

Notice that this class derives from *BaseView* so all properties from the parent class can be overriden also.

Implement *form_get* and *form_post* to implement your form pre-processing and post-processing

Most importante Base Properties:

:form_title: The title to be presented (this is mandatory)
:form_columns: The form column names to include
:form: Your form class (WTFORM) (this is mandatory) 
    

