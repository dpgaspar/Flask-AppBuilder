Actions
=======

Define your view
----------------

You can setup your actions on records on the show or list views.
This is a powerful feature, you can easily add custom functionality to your db records,
like mass delete, sending emails with record information, special mass update etc.

Just use the @action decorator on your own functions. Here's an example

::

    from flask_appbuilder.actions import action
    from flask_appbuilder import ModelView
    from flask_appbuilder.models.sqla.interface import SQLAInterface
    from flask import redirect

    class GroupModelView(ModelView):
        datamodel = SQLAInterface(Group)
        related_views = [ContactModelView]
	
        @action("myaction","Do something on this record","Do you really want to?","fa-rocket")
        def myaction(self, item):
            """
                do something with the item record
            """
            return redirect(self.get_redirect())
   
This will create the necessary permissions for the item,
so that you can include or remove them from a particular role.

You can easily implement a massive delete option on lists. Just add the following code
to your view. This example will tell F.A.B. to implement the action just for list views and not
show the option on the show view. You can do this by disabling the *single* or *multiple*
parameters on the **@action** decorator.

::

        @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
        def muldelete(self, items):
            self.datamodel.delete_all(items)
            self.update_redirect()
            return redirect(self.get_redirect())


F.A.B will call your function with a list of record items if called from a list view.
Or a single item if called from a show view. By default an action will be implemented on
list views and show views so your method's should be prepared to handle a list of records or
a single record::

        @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
        def muldelete(self, items):
            if isinstance(items, list):
                self.datamodel.delete_all(items)
                self.update_redirect()
            else:
                self.datamodel.delete(items)
            return redirect(self.get_redirect())
