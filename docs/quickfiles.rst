Quick Files and Images
======================

You can implement views with images or files associated

Define your model (models.py)
----------------------------------

::

    class Person(BaseMixin, Base):
        id = Column(Integer, primary_key=True)
        name = Column(String(150), unique = True, nullable=False)    	
        photo = Column(ImageColumn, nullable=False )
    
        def photo_img(self):
    	    im = ImageManager()
            if self.photo:
                return Markup('<a href="/persongeneralview/show/' + str(self.id) + '" class="thumbnail"><img src="' + im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
            else:
                return Markup('<a href="/persongeneralview/show/' + str(self.id) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        
Notice:

The "ImageColumn" type, this is an extended type from Flask-AppBuilder.

Define your Views (views.py)
----------------------------

::

    class PersonGeneralView(GeneralView):
        datamodel = SQLAModel(Person, db.session)

        list_widget = ListThumbnail

        label_columns = {'name':'Name','photo':'Photo','photo_img':'Photo'}
        list_columns = ['photo_img', 'name']
        show_columns = ['photo_img','name']

Notice:

We are overriding the list_widget, the widget that is normally used by GeneralView. This will display a thumbnail list excellent for displaying images.

And that's it! Images will be saved on the server and has UUID's and will be resized for optimization.

Next step
---------

Take a look at the example:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickimages

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickfiles

Some images:

.. image:: ./images/images_list.png
    :width: 100%
