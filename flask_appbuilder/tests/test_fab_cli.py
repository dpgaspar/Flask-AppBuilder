import glob
import json
import logging
import os
import tempfile
from unittest.mock import ANY, patch

from click.testing import CliRunner
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.cli import (
    cast_int_like_to_int,
    create_app,
    create_permissions,
    create_user,
    export_roles,
    import_roles,
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

    def test_cast_int_like_to_int(self):
        scenarii = {
            -1: -1,
            0: 0,
            1: 1,
            "-1": -1,
            "0": 0,
            "1": 1,
            "+1": 1,
            "foo": "foo",
            None: None,
        }

        for input, expected_output in scenarii.items():
            self.assertEqual(cast_int_like_to_int(input), expected_output)


class SQLAlchemyImportExportTestCase(FABTestCase):
    def setUp(self):
        with open("flask_appbuilder/tests/data/roles.json", "r") as fd:
            self.expected_roles = json.loads(fd.read())

    def test_export_roles(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            app = Flask("src_app")
            app.config.from_object("flask_appbuilder.tests.config_security")
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite:///{os.path.join(tmp_dir, 'src.db')}"
            db = SQLA(app)
            app_builder = AppBuilder(app, db.session)  # noqa: F841
            cli_runner = app.test_cli_runner()

            path = os.path.join(tmp_dir, "roles.json")

            export_result = cli_runner.invoke(export_roles, [f"--path={path}"])

            self.assertEqual(export_result.exit_code, 0)
            self.assertTrue(os.path.exists(path))

            with open(path, "r") as fd:
                resulting_roles = json.loads(fd.read())

            for expected_role in self.expected_roles:
                match = [
                    r for r in resulting_roles if r["name"] == expected_role["name"]
                ]
                self.assertTrue(match)
                resulting_role = match[0]
                resulting_role_permission_view_menus = {
                    (pvm["permission"]["name"], pvm["view_menu"]["name"])
                    for pvm in resulting_role["permissions"]
                }
                expected_role_permission_view_menus = {
                    (pvm["permission"]["name"], pvm["view_menu"]["name"])
                    for pvm in expected_role["permissions"]
                }
                self.assertEqual(
                    resulting_role_permission_view_menus,
                    expected_role_permission_view_menus,
                )

    def test_export_roles_filename(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            app = Flask("src_app")
            app.config.from_object("flask_appbuilder.tests.config_security")

            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite:///{os.path.join(tmp_dir, 'src.db')}"
            db = SQLA(app)
            app_builder = AppBuilder(app, db.session)  # noqa: F841

            owd = os.getcwd()
            os.chdir(tmp_dir)
            cli_runner = app.test_cli_runner()
            export_result = cli_runner.invoke(export_roles)
            os.chdir(owd)

            self.assertEqual(export_result.exit_code, 0)
            self.assertGreater(
                len(glob.glob(os.path.join(tmp_dir, "roles_export_*"))), 0
            )

    @patch("json.dumps")
    def test_export_roles_indent(self, mock_json_dumps):
        """Test that json.dumps is called with the correct argument passed from CLI."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            app = Flask("src_app")
            app.config.from_object("flask_appbuilder.tests.config_security")
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite:///{os.path.join(tmp_dir, 'src.db')}"
            db = SQLA(app)
            app_builder = AppBuilder(app, db.session)  # noqa: F841
            cli_runner = app.test_cli_runner()

            cli_runner.invoke(export_roles)
            mock_json_dumps.assert_called_with(ANY, indent=None)
            mock_json_dumps.reset_mock()

            example_cli_args = ["", "foo", -1, 0, 1]
            for arg in example_cli_args:
                cli_runner.invoke(export_roles, [f"--indent={arg}"])
                mock_json_dumps.assert_called_with(ANY, indent=arg)
                mock_json_dumps.reset_mock()

    def test_import_roles(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            app = Flask("dst_app")
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite:///{os.path.join(tmp_dir, 'dst.db')}"
            db = SQLA(app)
            app_builder = AppBuilder(app, db.session)
            cli_runner = app.test_cli_runner()

            path = os.path.join(tmp_dir, "roles.json")

            with open(path, "w") as fd:
                fd.write(json.dumps(self.expected_roles))

            # before import roles on dst app include only Admin and Public
            self.assertEqual(len(app_builder.sm.get_all_roles()), 2)

            import_result = cli_runner.invoke(import_roles, [f"--path={path}"])
            self.assertEqual(import_result.exit_code, 0)

            resulting_roles = app_builder.sm.get_all_roles()

            for expected_role in self.expected_roles:
                match = [r for r in resulting_roles if r.name == expected_role["name"]]
                self.assertTrue(match)
                resulting_role = match[0]

                expected_role_permission_view_menus = {
                    (pvm["permission"]["name"], pvm["view_menu"]["name"])
                    for pvm in expected_role["permissions"]
                }
                resulting_role_permission_view_menus = {
                    (pvm.permission.name, pvm.view_menu.name)
                    for pvm in resulting_role.permissions
                }
                self.assertEqual(
                    resulting_role_permission_view_menus,
                    expected_role_permission_view_menus,
                )
