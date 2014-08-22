Installation
============

Installation is straightforward, using the normal python package install.
I do advise you to additionally install the base skeleton application
so that you can immediately have a running application (without any models yet) and an easy to grow boilerplate.

Checkout installation video on `YouTube <http://youtu.be/ZrqFDroqqWE>`_

.. note::

	Remember the initial user is **'admin'** password **'general'**.

Using pip
---------

- **Simple Install**

    You can install the framework simply by::

	$ pip install flask-appbuilder

- **Advised Virtual Environment Install**

    Virtual env is highly advisable because the more projects you have,
    the more likely it is that you will be working with
    different versions of Python itself, or at least different versions of Python libraries.
    Let’s face it: quite often libraries break backwards compatibility,
    and it’s unlikely that any serious application will have zero dependencies.
    So what do you do if two or more of your projects have conflicting dependencies?

    If you are on Mac OS X or Linux, chances are that one of the following two commands will work for you:

    ::

        $ sudo easy_install virtualenv

    or even better:

    ::

        $ sudo pip install virtualenv

    One of these will probably install virtualenv on your system.
    Maybe it’s even in your package manager. If you use a debian system (like Ubuntu), try:

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

    Now install F.A.B on the virtual env,
    it will install all the dependencies and these will be isolated from your system's python packages

    ::

        (venv)$ pip install flask-appbuilder


Skeleton Application
--------------------

After installing F.A.B. you probably want a simple quick start.
You can use one of the examples, or clone the base skeleton application::

    $ git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git
    $ cd Flask-AppBuilder-Skeleton


This is a running boilerplate. You can simply run it on a development server, like this::

    $ python run.py

That's it!! When you run the development server you may notice the log,
informing you about creating all the needed security tables,
creating the initial 'admin' user, roles, as well as all the minimal permissions.

You now have a running development server on http://localhost:8080.

The git clone of the skeleton is not actually needed for you to run AppBuilder, but it's a good way to start.

Initialization
--------------

When starting your application for the first time,
all AppBuilder security tables will be created for you.
All your models can easily be created too (optionally).

**The initial 'admin' user password will be 'general'**. Change it on your first access using the application.
(Click the username on the navigation bar, then choose 'Reset Password')

Installation Requirements
-------------------------

pip installs all the requirements for you.

Flask App Builder dependes on

    - flask : The web framework, this is what we're extending.
    - flask-sqlalchemy : DB access (see SQLAlchemy).
    - flask-login : Login, session on flask.
    - flask-openid : Open ID authentication.
    - flask-wtform : Web forms.
    - flask-BabelPkg : For internationalization, fork from flask-babel.

If you plan to use Image on database, you will need to install PIL::

    pip install pillow
    
or::

    pip install PIL


Python 2 and 3 Compatibility
----------------------------

The framework itself is compatible and has been tested for Python 2.6, 2.7 and 3.3.
But there is still one problem in Python 3.3, the framework internationalization feature
uses the excellent package Babel, but i've found an incompatibility on it for python 3.3.
While this problem is not solved there is a limitation for Py3.3 on F.A.B. you can't use
Babel's features, so on config you must only setup english::

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_FOLDER = 'translations'
    LANGUAGES = {
        'en':{'flag':'gb','name':'English'}
    }
