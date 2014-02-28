Quick Files and Images
======================

You can implement views with images or files associated

Define your model (models.py)
-----------------------------

::

    class Person(BaseMixin, Base):
        id = Column(Integer, primary_key=True)
        name = Column(String(150), unique = True, nullable=False)    	
        photo = Column(ImageColumn, nullable=False )
    
        def photo_img(self):
    	    im = ImageManager()
            if self.photo:
                return Markup('<a href="' + url_for('PersonGeneralView.show',pk=str(self.id)) + '" class="thumbnail"><img src="' + im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
            else:
                return Markup('<a href="' + url_for('PersonGeneralView.show',pk=str(self.id)) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        
Create an additional method in this case *photo_img* to inject your own custom HTML to show your saved images. In this example we are showing the images and linking them with the show view.

Later reference this method like it's a column on your view.

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

We are overriding the *list_widget*, the widget that is normally used by GeneralView. This will display a thumbnail list excelent for displaying images.

Notice that we are not using the *image* column but the method *photo_img* we have created that will display the image and link it to the show view.

And that's it! images will be saved on the server has UUID's and will be resized for optimization.

Next step
---------

Take a look at the example:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickimages

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickfiles

Some images:

.. image:: ./images/images_list.png
    :width: 100%
