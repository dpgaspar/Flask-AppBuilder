Quick Minimal Application
=========================

How to setup a minimal Application
----------------------------------

::

    import os
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext.appbuilder.baseapp import BaseApp

    # init Flask
    app = Flask(__name__)

    # Basic config with security for forms and session cookie
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = 'thisismyscretkey'

    # Init SQLAlchemy
    db = SQLAlchemy(app)
    # Init F.A.B.
    genapp = BaseApp(app, db)

    # Run the development server
    app.run(host='0.0.0.0', port=8080, debug=True)


If you run this, notice that your database will be created with two roles 'Admin' and 'Public', as well has all the security detailed permissions.

The default authentication method will be database, you can take a look of all your application options on :doc:`config`

The downside of using a minimal configuration like this, is that you loose all the translations (Babel) of the security views and menus setuped initialy by AppBuilder

Please take a look at github `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_
