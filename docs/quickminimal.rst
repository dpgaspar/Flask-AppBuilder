Quick Minimal Application
=========================

How to setup a minimal Application
----------------------------------

This is the most basic example, using the minimal code needed to setup a running application with F.A.B.

Will use sqlite for the database no need to install anything.
Notice the SQLA class this is just a child class from flask.ext.SQLAlchemy that overrides the declarative base
to F.A.B. You can use every configuration and method from flask extension except the model's direct query.

I do advise using the skeleton application as described on the :doc:`installation`

::

    import os
    from flask import Flask
    from flask_appbuilder import SQLA, AppBuilder

    # init Flask
    app = Flask(__name__)

    # Basic config with security for forms and session cookie
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = 'thisismyscretkey'

    # Init SQLAlchemy
    db = SQLA(app)
    # Init F.A.B.
    appbuilder = AppBuilder(app, db.session)

    # Run the development server
    app.run(host='0.0.0.0', port=8080, debug=True)


If you run this, notice that your database will be created with two roles 'Admin' and 'Public',
as well has all the security detailed permissions.

The default authentication method will be database, and you can initially login with **'admin'/'general'**.
you can take a look at all your configuration options on :doc:`config`

Take a look at this `example <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickminimal>`_ on Github
