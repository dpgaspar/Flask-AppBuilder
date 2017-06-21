Model Views on MongoDB
======================

Last chapter we created a very simple contacts application, we are going to do the same, this time
using MongoDB. Remember you should use the correct app skeleton, the one for MongoDB, this way
the security models will be created on the MongoDB and not on SQLLite by default, take a look
at the way that AppBuilder is initialized.

And the source code for this chapter on
`examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/mongoengine>`_

Initialization
--------------

Initialization with MongoDB is a bit different, we must tell F.A.B. to use a different SecurityManager.

On __init__.py::

    import logging
    from flask import Flask
    from flask_appbuilder import AppBuilder
    from flask_appbuilder.security.mongoengine.manager import SecurityManager
    from flask_mongoengine import MongoEngine

    logging.getLogger().setLevel(logging.DEBUG)

    app = Flask(__name__)
    app.config.from_object('config')
    dbmongo = MongoEngine(app)
    # The Flask-AppBuilder init
    appbuilder = AppBuilder(app, security_manager_class=SecurityManager)

    from app import models, views


AppBuilder is initialized with the *security_manager_class* parameter with a SecurityManager class for MongoDB.
All security models are created on MongoDB. Notice also that no db.session is passed to AppBuilder there is
no *session* on MongoDB.

Define your models (models.py)
------------------------------

We are going to define two extra models from the previous example, just for fun.

The *ContactGroup* model.

::

    from mongoengine import Document
    from mongoengine import DateTimeField, StringField, ReferenceField, ListField

    class ContactGroup(Document):
        name = StringField(max_length=60, required=True, unique=True)

        def __unicode__(self):
            return self.name

        def __repr__(self):
            return self.name

The *Contacts* *Gender* and Tags models.

::

    class Gender(Document):
        name = StringField(max_length=60, required=True, unique=True)

        def __unicode__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __str__(self):
            return self.name


    class Tags(Document):
        name = StringField(max_length=60, required=True, unique=True)

        def __unicode__(self):
            return self.name


    class Contact(Document):
        name = StringField(max_length=60, required=True, unique=True)
        address = StringField(max_length=60)
        birthday = DateTimeField()
        personal_phone = StringField(max_length=20)
        personal_celphone = StringField(max_length=20)
        contact_group = ReferenceField(ContactGroup, required=True)
        gender = ReferenceField(Gender, required=True)
        tags = ListField(ReferenceField(Tags))


Notice how the relations many to one and many to many are made, the framework still only supports this kind
of normalized schemas.

Define your Views (views.py)
----------------------------

Now we are going to define our view for *ContactGroup* model.
This view will setup functionality for create, remove, update and show primitives for your model's definition.

Inherit from *ModelView* class that inherits from *BaseCRUDView* that inherits from *BaseModelView*,
so you can override all their public properties to configure many details for your CRUD primitives.
take a look at :doc:`advanced`.

::

    from flask_appbuilder import ModelView
    from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface

    class GroupModelView(ModelView):
        datamodel = MongoEngineInterface(ContactGroup)
        related_views = [ContactModelView]


The ContactModelView ? (that was a reference in *related_views* list)

Let's define it::

    class ContactModelView(ModelView):
        datamodel = MongoEngineInterface(Contact)

        label_columns = {'contact_group':'Contacts Group'}
        list_columns = ['name','personal_celphone','birthday','contact_group']

        show_fieldsets = [
            ('Summary',{'fields':['name','address','contact_group']}),
            ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
            ]


Register (views.py)
-------------------

Register everything, to present the models and create the menu.

::

        appbuilder.add_view(GroupModelView, "List Groups",icon = "fa-folder-open-o",category = "Contacts",
                        category_icon = "fa-envelope")
        appbuilder.add_view(ContactModelView, "List Contacts",icon = "fa-envelope",category = "Contacts")

Take a look at the :doc:`api` for add_view method.

As you can see, you register and define your Views exactly the same way as with SQLAlchemy. You can even use both.


