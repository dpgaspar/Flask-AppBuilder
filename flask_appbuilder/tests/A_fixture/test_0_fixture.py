from datetime import datetime

from flask_appbuilder import SQLA
from hiro import Timeline

from ..base import FABTestCase
from ..const import (
    MODEL1_DATA_SIZE,
    PASSWORD_ADMIN,
    PASSWORD_READONLY,
    USERNAME_ADMIN,
    USERNAME_READONLY,
)
from ..sqla.models import insert_data


class TestData(FABTestCase):
    def setUp(self):
        from flask import Flask

        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_data(self):
        with Timeline(start=datetime(2020, 1, 1), scale=0).freeze():
            insert_data(self.db.session, MODEL1_DATA_SIZE)

    def test_create_admin(self):
        with Timeline(start=datetime(2020, 1, 1), scale=0).freeze():
            self.create_admin_user(self.appbuilder, USERNAME_ADMIN, PASSWORD_ADMIN)

    def test_create_ro_user(self):
        with Timeline(start=datetime(2020, 1, 1), scale=0).freeze():
            self.create_user(
                self.appbuilder,
                USERNAME_READONLY,
                PASSWORD_READONLY,
                "ReadOnly",
                first_name="readonly",
                last_name="readonly",
                email="readonly@fab.org",
            )
