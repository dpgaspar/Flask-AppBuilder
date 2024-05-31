import logging
import os

from tests.base import FABTestCase
from tests.fixtures.addon_manager import DummyAddOnManager


log = logging.getLogger(__name__)


class FlaskTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config["ADDON_MANAGERS"] = [
            "tests.fixtures.addon_manager.DummyAddOnManager"
        ]
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.appbuilder = AppBuilder(self.app)

    def tearDown(self):
        self.ctx.pop()
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_addon_import(self):
        self.assertIsInstance(
            self.appbuilder.addon_managers[
                "tests.fixtures.addon_manager.DummyAddOnManager"
            ],
            DummyAddOnManager,
        )

    def test_addon_register_views(self):
        client = self.app.test_client()
        rv = client.get("/dummy/method1/test1")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data.decode("utf-8"), "test1")
