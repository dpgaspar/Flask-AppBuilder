Quick Minimal Application
=========================

How to setup a minimal Application
----------------------------------

The module imports::

    import os
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    from sqlalchemy.engine import Engine
    from flask.ext.appbuilder.baseapp import BaseApp

The code it self::

    basedir = os.path.abspath(os.path.dirname(__file__))
    
    """
        The Flask initialization
    """
    app = Flask(__name__)
    
more::

    """
        Your database connection String
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'a$
    app.config['CSRF_ENABLED'] = True

more::

    """
        Secret key for authentication cookies
    """
    app.config['SECRET_KEY'] = 'thisismyscretkey'
    """
        The Flask-SQLAlchemy object initialization with the SQLALCHEMY_DATABASE_URI string you have setup 
    """
    db = SQLAlchemy(app)
    
more::
    
    """
        The Base Flask-AppBuilder object initialization
    """
    genapp = BaseApp(app, db)
    
more::
    
    """
        Run the application has a developement web server
    """
    app.run(host='0.0.0.0', port=8080, debug=True)
    
If you run this, notice that your database will be created with two roles 'Admin' and 'Public', as well has all the security detailed permissions.

The default authentication method will be database, you can take a look of all your application options on :doc:`config`

The downside of using a minimal configuration like this, is that you loose all the translations (Babel) of the security views and menus setuped initialy by AppBuilder

Please take a look at github `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_
