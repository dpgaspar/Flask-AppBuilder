Installation
============

Using pip
---------

- Simple Install::

	$ pip install flask-appbuilder

- Advised Virtual Env Install::

    Virtual env is highly advisable because the more projects you have, the more likely it is that you will be working with different versions of Python itself, or at least different versions of Python libraries. Let’s face it: quite often libraries break backwards compatibility, and it’s unlikely that any serious application will have zero dependencies. So what do you do if two or more of your projects have conflicting dependencies?

    If you are on Mac OS X or Linux, chances are that one of the following two commands will work for you:

    ::

        $ sudo easy_install virtualenv

    or even better:

    ::

        $ sudo pip install virtualenv

    One of these will probably install virtualenv on your system. Maybe it’s even in your package manager. If you use Ubuntu, try:

    ::

        $ sudo apt-get install python-virtualenv

    Once you have virtualenv installed, :

    ::

        $ mkdir myproject
        $ cd myproject
        $ virtualenv venv
        New python executable in venv/bin/python
        Installing distribute............done.
        $ . venv/bin/activate
        (venv)$

    Now install F.A.B on the virtual env, it will install all the dependencies and these will be isolated from your system's python packages

    ::

        $ pip install flask-appbuilder


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

