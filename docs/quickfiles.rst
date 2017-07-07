Model Views with Files and Images
=================================

You can implement views with images or files embedded on the model's definition. You can do it using SQLAlchemy or
MongoDB (MongoEngine). When using SQLAlchemy, files and images are saved on the filesystem, on MongoDB on the db (GridFS).

Define your model (models.py)
-----------------------------

::

    from flask_appbuilder import Model
    from flask_appbuilder.models.mixins import ImageColumn

    class Person(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(150), unique = True, nullable=False)    	
        photo = Column(ImageColumn(size=(300, 300, True), thumbnail_size=(30, 30, True)))
    
        def photo_img(self):
    	    im = ImageManager()
            if self.photo:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                 '" class="thumbnail"><img src="' + im.get_url(self.photo) +\
                  '" alt="Photo" class="img-rounded img-responsive"></a>')
            else:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                 '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')

        def photo_img_thumbnail(self):
    	    im = ImageManager()
            if self.photo:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                 '" class="thumbnail"><img src="' + im.get_url_thumbnail(self.photo) +\
                  '" alt="Photo" class="img-rounded img-responsive"></a>')
            else:
                return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                 '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')


Create two additional methods in this case *photo_img* and *photo_img_thumbnail*, to inject your own custom HTML,
to show your saved images. In this example the customized method is showing the images, and linking them with the show view.
Notice how the methods are calling *get_url* and *get_url_thumbnail* from ImageManager, these are returning the
url for the images, each image is saved on the filesystem using the global config **IMG_UPLOAD_FOLDER**.
Each image will have two files with different sizes, images are saved as <uuid>_sep_<filename>, and <uuid>_sep_<filename>_thumb

.. note::
    The "ImageColumn" type, is an extended type from Flask-AppBuilder.

Later reference this method like it's a column on your view.

To implement image or file support using GridFS from MongoDB is even easier, take a look at the example:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/mongoimages

Define your Views (views.py)
----------------------------

::

    from flask_appbuilder import ModelView
    from flask_appbuilder.models.sqla.interface import SQLAInterface

    class PersonModelView(ModelView):
        datamodel = SQLAInterface(Person)

        list_widget = ListThumbnail

        label_columns = {'name':'Name','photo':'Photo','photo_img':'Photo', 'photo_img_thumbnail':'Photo'}
        list_columns = ['photo_img_thumbnail', 'name']
        show_columns = ['photo_img','name']

We are overriding the *list_widget*, the widget that is normally used by ModelView.
This will display a thumbnail list, excellent for displaying images.

We're not using the *image* column but the methods *photo_img* and *photo_img_thumbnail* we have created.
These methods will display the images and link them to show view.

And that's it! images will be saved on the server.
Their file names will result in the concatenation of UUID with their original name. They will be resized for optimization.

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
