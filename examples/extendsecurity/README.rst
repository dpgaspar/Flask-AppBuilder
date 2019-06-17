Filtered data Example
---------------------


Simple contacts application where contacts are filtered by the user's company who has created them.
The user only "sees" his/her companies contacts. It also extends the User Model adding a company relationship and
employee number.

Insert test data::

    $ python testdata.py

testdata will create 3 users for you to play with, these are:

- user1_company1

- user2_company2

- user3_company2

Their passwords are 'password'

Run it::

    $ export FLASK_APP="app:create_app('config')"
    $ flask fab create-admin
    $ flask fab create-permissions
    $ flask run

