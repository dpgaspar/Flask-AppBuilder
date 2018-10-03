Installation
============

Installation is straightforward, using the normal python package install.
I do advise you to additionally install the base skeleton application
so that you can immediately have a running application (without any models yet) and an easy to grow boilerplate.

Checkout installation video on `YouTube <http://youtu.be/xvum4vfwldg>`_

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

    Next create a virtualenv:

    ::

        $ virtualenv venv
        New python executable in venv/bin/python
        Installing distribute............done.
        $ . venv/bin/activate
        (venv)$

    Now install F.A.B on the virtual env,
    it will install all the dependencies and these will be isolated from your system's python packages

    ::

        (venv)$ pip install flask-appbuilder


    Once you have virtualenv installed, use **fabmanager** the command line tool to create your first app.
    So create a skeleton application and the first admin user:

    ::

        (venv)$ fabmanager create-app
        Your new app name: first_app
        Your engine type, SQLAlchemy or MongoEngine [SQLAlchemy]:
        Downloaded the skeleton app, good coding!
        (venv)$ cd first_app
        (venv)$ fabmanager create-admin
        Username [admin]:
        User first name [admin]:
        User last name [user]:
        Email [admin@fab.org]:
        Password:
        Repeat for confirmation:

    .. note:: There are two type of skeletons available you can choose from SQLAlchemy default or MongoEngine for
            MongoDB. **To use the MongoEngine skeleton you need to install flask-mongoengine extension.**

    The framework will immediately insert all possible permissions on the database, these will be associated with
    the *Admin* role that belongs to the *admin* user you just created. Your ready to run:

    ::

        (venv)$ fabmanager run

    This will start a web development server

    You now have a running development server on http://localhost:8080.

    The skeleton application is not actually needed for you to run AppBuilder, but it's a good way to start.
    This first application is SQLAlchemy based.

Initialization
--------------

When starting your application for the first time,
all AppBuilder security tables will be created for you.
All your models can easily be created too (optionally).

.. note:: Since version 1.3.0 no admin user is automatically created, you must use **fabmanager** to do it.
    There are lot's of other useful options you can use with **fabmanager** like reset user's password,
    list all your users and views, etc.

Installation Requirements
-------------------------

pip installs all the requirements for you.

Flask App Builder dependes on

    - flask : The web framework, this is what we're extending.
    - flask-sqlalchemy : DB access (see SQLAlchemy).
    - flask-login : Login, session on flask.
    - flask-openid : Open ID authentication.
    - flask-wtform : Web forms.
    - flask-Babel : For internationalization.

If you plan to use Image processing or upload, you will need to install PIL::

    pip install pillow

or::

    pip install PIL


Python 2 and 3 Compatibility
----------------------------

The framework itself is compatible and has been tested for Python 2.7 and 3.3.
But there is still one problem in Python 3.3, the framework internationalization feature
uses the excellent package Babel, but i've found an incompatibility on it for python 3.3.
While this problem is not solved there is a limitation for Py3.3 on F.A.B. you can't use
Babel's features, so on config you must only setup english::

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_FOLDER = 'translations'
    LANGUAGES = {
        'en':{'flag':'gb','name':'English'}
    }
