Instalation
===========

2 Step instalation
----------------------

- Install it::

	pip install flask-appbuilder
	git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git

- Run it::

    cd Flask-AppBuilder-Skeleton
	python run.py

That's it!!

The git clone is not actually needed for you to run AppBuilder. but it's a good way to start, also comes with all the translations from the framework see :doc:`i18n`

What requirements were instaled
-------------------------------

pip instalations installs all the requirements for you.

Flask App Builder dependes on

    - flask : The web framework, this is what were extending
    - flask-sqlalchemy : DB access see SQLAlchemy, This requirement is optional
    - flask-login : Login, session on flask.
    - flask-openid : Open ID authentication
    - flask-wtform
    - flask-Babel : For internationalization

If you plan to use Image on database, you will need to install PIL::

    pip install pillow
    
or::

    pip install PIL

Initialization
--------------

When starting your application for the first time, all your models and AppBuilder security tables will be created for you.
Version 0.3.X does not need you to run "init_app.py". AppBuilder will create all available permissions associated with your views and menus, and these will be automaticaly associated with your defined role AUTH_ROLE_ADMIN
 
The 'admin' password will be 'general'. Change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')
