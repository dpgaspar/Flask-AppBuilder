Filtered data Example
---------------------


Simple contacts application where contacts are filtered by the user's company who has created them.
The user only "sees" his/her companies contacts. It also extends the User Model adding a company relationship and
employee number.

Insert test data::

    $ python testdata.py

testdata will create 3 users for you to play with, these are:

user1
user2
user3

Their passwords are 'password'

Run it::

    $ fabmanager run


