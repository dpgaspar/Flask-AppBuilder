Quick How to Example
--------------------

Simple contacts application with flask-migrate.

Use of Flask-Migrate (Use Flask>0.11.0)::

    $ export FLASK_APP=app/__init__.py
    $ flask db init
    $ flask db migrate
    # Check the migration script
    $ flask db upgrate --sql
    $ flask db upgrade

Insert test data::

    $ python testdata.py

Run it::

    $ export FLASK_APP=app/__init__.py
    $ flask fab create-admin
    $ flask run

