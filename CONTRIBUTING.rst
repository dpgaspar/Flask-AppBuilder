Contributing
------------

Contributions are very welcome and highly appreciated!

Setup you dev environment
-------------------------

1 - First create a python development virtualenv

.. code-block:: bash

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements/base.txt -r requirements/dev.txt -r requirements/extra.txt

2 - Install `docker` and `docker-compose`

Run tests
---------

Contributions for new features or fixes should have tests associated. To verify that all tests are green you
can run a subset of tests targeting only Postgres.

1 - Start Postgres

.. code-block:: bash

    $ docker-compose up -d

2 - Run Postgres tests

.. code-block:: bash

    $ nose2 -c setup.cfg -A '!mongo' tests

You can also use tox

.. code-block:: bash

    $ tox -e postgres

4 - Code Formatting

.. code-block:: bash

    $ black flask_appbuilder tests
    $ flake8 flask_appbuilder tests

Run a single test
-----------------

Using Postgres

1 - Stop and delete Postgres volume, then restart

.. code-block:: bash

    $ docker-compose down -v
    $ docker-compose up -d

2 - Export the connection string

.. code-block:: bash

   $ export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://pguser:pguserpassword@0.0.0.0/app

4 - To run a single test

.. code-block:: bash

    $ nose2 -v tests.test_api.APITestCase.test_get_item_dotted_mo_notation

.. note::

    If your using SQLite3, the location of the db is: ./tests/app.db
    You can safely delete it, if you need to delete test data for example.


Responsible disclosure of Security Vulnerabilities
--------------------------------------------------

We want to keep Flask-AppBuilder safe for everyone. If you've discovered a security vulnerability
please report to danielvazgaspar@gmail.com.
Reporting security vulnerabilities through the usual GitHub Issues channel
is not ideal as it will publicize the flaw before a fix can be applied.
