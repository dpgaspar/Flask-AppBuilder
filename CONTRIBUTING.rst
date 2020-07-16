Contributing
------------

Contributions are very welcome and highly appreciated!

Setup you dev environment
-------------------------

1 - First create a python development virtualenv

.. code-block:: bash

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt -r requirements-dev.txt

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

    $ tox -e postgres
