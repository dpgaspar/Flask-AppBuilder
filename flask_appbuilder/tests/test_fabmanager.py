from nose.tools import eq_, ok_, raises
import unittest
import os
import string
import random
import datetime

import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)



class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        log.debug("TEAR DOWN")


    def test_create_app(self):
        """
            Test create app
        """
        out = os.popen('fabmanager create-app --name myapp --engine SQLAlchemy').read()
        ok_("Downloaded the skeleton app, good coding!" in out)


        

