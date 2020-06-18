import logging
import os

from click.testing import CliRunner
from flask_appbuilder.cli import (
    create_app,
    create_permissions,
    create_user,
    list_users,
    list_views,
    reset_password,
)

from .base import FABTestCase

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

APP_DIR = "myapp"


class FlaskTestCase(FABTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        log.debug("TEAR DOWN")

    def test_create_app(self):
        """
            Test create app, create-user
        """
        os.environ["FLASK_APP"] = "app:app"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                create_app, [f"--name={APP_DIR}", "--engine=SQLAlchemy"]
            )
            self.assertIn("Downloaded the skeleton app, good coding!", result.output)
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
            self.assertIn("User bob created.", result.output)

            result = runner.invoke(list_users, [])
            self.assertIn("bob", result.output)

            runner.invoke(create_permissions, [])

            runner.invoke(reset_password, ["--username=bob", "--password=bar"])

    def test_list_views(self):
        """
            CLI: Test list views
        """
        os.environ["FLASK_APP"] = "app:app"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(list_views, [])
            self.assertIn("List of registered views", result.output)
            self.assertIn(" Route:/api/v1/security", result.output)
