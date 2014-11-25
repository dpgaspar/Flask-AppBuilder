Model Views with Files and Images
=================================

You can implement views with images or files embedded on the model's definition

Define your model (models.py)
-----------------------------

::

    class Person(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(150), unique = True, nullable=False)    	
        photo = Column(ImageColumn, nullable=False )
    
        def photo_img(self):
    	    im = ImageManager()
            if self.photo:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) + '" class="thumbnail"><img src="' + im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
            else:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        
Create an additional method in this case *photo_img*, to inject your own custom HTML, to show your saved images. In this example the customized method is showing the images, and linking them with the show view.

Later reference this method like it's a column on your view.

.. note::
    The "ImageColumn" type, is an extended type from Flask-AppBuilder.

Define your Views (views.py)
----------------------------

::

    class PersonModelView(ModelView):
        datamodel = SQLAModel(Person)

        list_widget = ListThumbnail

        label_columns = {'name':'Name','photo':'Photo','photo_img':'Photo'}
        list_columns = ['photo_img', 'name']
        show_columns = ['photo_img','name']

Notice that we are overriding the *list_widget*, the widget that is normally used by ModelView. This will display a thumbnail list, excellent for displaying images.

We are not using the *image* column but the method *photo_img* we have created. This method will display the image and link it to the show view.

And that's it! images will be saved on the server. Their file names will result in the concatenation of UUID with their original name. They will be resized for optimization.

.. note::
    You can define image resizing using configuration key *IMG_SIZE*

We are overriding the list_widget, the widget that is normally used by ModelView. This will display a thumbnail list excellent for displaying images.

And that's it! Images will be saved on the server with their filename concatenated by a UUID's. Aditionally will be resized for optimization.

Next step
---------

Take a look at the example:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickimages

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickfiles

Some images:

.. image:: ./images/images_list.png
    :width: 100%
