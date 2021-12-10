AddOn development
=================

Using AddOn's with the framework it is a great way to develop your application
and make public open source contributions to the community.

With it you can use a more modular design on your application, you can add functionality,
views and models that you can build independently and install or uninstall (using different versions).

To start building your own AddOn's you can use issue the following command::


    $ flask fab create-addon --name first


Your addon name will be prefixed by 'fab_addon_' so this addon would be called **fab_addon_first**.
The create-addon will download a default skeleton addon for you to start more easily to code (much like the create-app
command).

The structure of the default base addon:

- <fab_addon_first>
   - setup.py: Setup installer use it to install your addon, or upload it to Pypi when your ready to release.
   - config.py: Used internaly by setup.py, this will make your setup more generic.
   - <fab_addon_first>
      - __init__.py: empty
      - models.py: Declare your addon's models (if any) just like on a normal app.
      - views.py: Declare your addon's views but don't register them here.
      - manager.py: This is where your addon manager will reside, It's your manager that will be imported by appbuilder.
      - version.py: Declare your addon version here, write your name (author), a small description and your email.

Your can use your addon much like a regular F.A.B. app, just don't instantiate anything (appbuilder, flask, SQLAlchemy etc...)
notice, __init__.py module is empty. So if you or anyone (if you upload your addon to pypi or make it public somewhere
like github) want to use your addon they just have to install it and declare it using the ADDON_MANAGERS key, this
key is a list of addon manager's.

So what is a manager? Manager is a class you declare that subclasses appbuilder BaseManager, and you have 4 important
methods you can override, there are:

:__init__(self, appbuilder): Manager's constructor. Good place to check for your addon's specific keys. For custom configuration
:register_views(self): Use it to register all your views and setup a menu for them (if you want to).
:pre_processs: Will be called before register_views. Good place to insert data into your models for example.
:post_process: Will be called after register_views.

A very simple manager would look something like this::


   import logging

   from flask_appbuilder.basemanager import BaseManager
   from flask_babel import lazy_gettext as _

   from .model import MyModel
   from .views import FirstModelView1


   log = logging.getLogger(__name__)


   class FirstAddOnManager(BaseManager):

       def __init__(self, appbuilder):
           """
                Use the constructor to setup any config keys specific for your app.
           """
           super(FirstAddOnManager, self).__init__(appbuilder)

       def register_views(self):
           """
               This method is called by AppBuilder when initializing, use it to add you views
           """
           self.appbuilder.add_view(FirstModelView1, "First View1",icon = "fa-user",category = "First AddOn")

       def pre_process(self):
           stuff = self.appbuilder.get_session.query(MyModel).filter(name == 'something').all()
           # process stuff

       def post_process(self):
           pass


How can you or someone use your AddOn? On the app config.py add this key::


   ADDON_MANAGERS = ['fab_addon_first.manager.FirstAddOnManager']

And thats it.

I've just added a simple audit modelViews's addon to start contributions and to serve as an example.

you can install it using::

   $ pip install fab_addon_audit

The source code is pretty simple, use it as an example to write your own:

https://github.com/dpgaspar/fab_addon_audit
