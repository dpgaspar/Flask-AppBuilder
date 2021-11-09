FactoryApp
----------

Simple example to show how to use a factory setup.

Create an Admin user and insert test data::

    $ python testdata.py

Run it::

    $ export FLASK_APP="app:create_app('config')"
    $ flask fab create-admin
    $ flask run

Try it. Open a browser to http://localhost:5000.

Using an alternate config::

    $ export FLASK_APP="app:create_app('config2')"
    $ flask fab create-admin
    $ flask run

