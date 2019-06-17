Filtered data Example
---------------------


Simple contacts application where contacts are filtered by the user who has created them.
The user only "sees" his/her contacts

Insert test data::

    $ python testdata.py

testdata will create 3 users for you to play with, these are:

user1
user2
user3

Their passwords are 'password'

Run it::

    $ export FLASK_APP=app/__init__.py
    $ flask fab create-admin
    $ flask run
