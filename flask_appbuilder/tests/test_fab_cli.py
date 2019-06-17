import logging
import os
import unittest

from click.testing import CliRunner
from flask_appbuilder.cli import create_app, create_user
from nose.tools import ok_


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

APP_DIR = 'myapp'


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        log.debug("TEAR DOWN")

    def test_create_app(self):
        """
            Test create app
        """
        os.environ['FLASK_APP'] = "app:app"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                create_app,
                [
                    f'--name={APP_DIR}',
                    '--engine=SQLAlchemy'
                ]
            )
            ok_("Downloaded the skeleton app, good coding!" in result.output)
            os.chdir(APP_DIR)
            result = runner.invoke(
                create_user,
                [
                    "--username=bob",
                    "--role=Public",
                    "--firstname=Bob",
                    "--lastname=Smith",
                    "--email=bob@fab.com",
                    "--password=foo",
                ],
            )
            log.info(result.output)
            ok_("User bob created." in result.output)
