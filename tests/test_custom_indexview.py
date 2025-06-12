import logging
import os

from flask_appbuilder import AppBuilder, IndexView
from tests.base import FABTestCase

log = logging.getLogger(__name__)


class CustomIndexView(IndexView):
    index_template = "templates/custom_index.html"


class FlaskTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask

        self.app = Flask(__name__, template_folder=".")
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")
        self.app.config[
            "FAB_INDEX_VIEW"
        ] = "tests.test_custom_indexview.CustomIndexView"

    def test_custom_indexview(self):
        """
        Test custom index view.
        """
        uri = "/"
        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app)
            client = self.app.test_client()
            rv = client.get(uri)

            self.assertEqual(rv.status_code, 200)
            data = rv.data.decode("utf-8")
            self.assertIn("This is a custom index view.", data)
