import os
import unittest

from flask_appbuilder import SQLA

from .base import FABTestCase
from .const import (
    MODEL1_DATA_SIZE,
    PASSWORD,
    USERNAME,
    PASSWORD_READONLY,
    USERNAME_READONLY,
)
from .sqla.models import insert_data


class TestData(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("flask_appbuilder.tests.config_api")
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_data(self):
        insert_data(self.db.session, MODEL1_DATA_SIZE)

    def test_create_admin(self):
        self.create_admin_user(self.appbuilder, USERNAME, PASSWORD)

    def test_create_ro_user(self):
        self.create_user(
            self.appbuilder,
            USERNAME_READONLY,
            PASSWORD_READONLY,
            "ReadOnly",
            first_name="readonly",
            last_name="readonly",
            email="readonly@fab.org",
        )
