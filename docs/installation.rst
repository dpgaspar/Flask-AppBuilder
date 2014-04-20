Installation
===========

Using pip
---------

- Install it::

	pip install flask-appbuilder
	
Skeleton Application
--------------------

If you want a simple quick start, you can use one of the examples, or clone the base skeleton application::

    git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git
    cd Flask-AppBuilder-Skeleton
    python run.py

That's it!!

The git clone is not actually needed for you to run AppBuilder. but it's a good way to start.

Initialization
--------------

When starting your application for the first time, all your models and AppBuilder security tables will be created for you.

**The 'admin' user password will be 'general'**. Change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')

What requirements were instaled
-------------------------------

pip installations installs all the requirements for you.

Flask App Builder dependes on

    - flask : The web framework, this is what were extending
    - flask-sqlalchemy : DB access see SQLAlchemy, This requirement is optional
    - flask-login : Login, session on flask.
    - flask-openid : Open ID authentication
    - flask-wtform
    - flask-BabelPkg : For internationalization, fork from flask-babel

If you plan to use Image on database, you will need to install PIL::

    pip install pillow
    
or::

    pip install PIL

