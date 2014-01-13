Actions
=======

You can setup your actions for records on the show page. Just use the @action decorator pointing to yout own function 

::

    from flask.ext.appbuilder.actions import action  

    class GroupGeneralView(GeneralView):
        datamodel = SQLAModel(Group, db.session)
        related_views = [ContactGeneralView()]
	
        @action("myaction","Do something on this record","","fa-rocket")
        def myaction(self, item):
            """
                do something with the item record
            """
            return redirect(url_for('.'))
   
This will create the necessary permissions for the item, so that you can include them or remove them from a particular role.

It will render a button for each action you define on the show page of *GeneralView*
