from nose.tools import eq_, ok_, raises
import unittest
import os
import string
import random
import datetime
import shutil
from flask_appbuilder.console import create_app, create_admin, create_user
from click.testing import CliRunner

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
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(create_app, input='myapp\nSQLAlchemy\n')
            ok_('Downloaded the skeleton app, good coding!' in result.output)

            with open('myapp/__init__.py', 'w') as f:
                for line in [
                    'from flask import Flask\n',
                    'from flask_appbuilder import AppBuilder, SQLA\n',
                    'app = Flask(__name__)\n',
                    'db = SQLA(app)\n',
                    'appbuilder = AppBuilder(app, db.session)\n',
                ]:
                    f.write(line)

            result = runner.invoke(create_user,[
                '--app=myapp', '--username=bob', '--role=Public', '--firstname=Bob',
                '--lastname=Smith', '--email=bob@fab.com', '--password=foo'])
            ok_('User bob created.' in result.output)

        with runner.isolated_filesystem():
            result = runner.invoke(create_app, input='myapp\nMongoEngine\n')
            ok_('Downloaded the skeleton app, good coding!' in result.output)
