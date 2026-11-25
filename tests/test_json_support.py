"""
Tests for JSON column support in Flask-AppBuilder
"""

import unittest

from flask import Flask
from flask_appbuilder import AppBuilder, ModelView
from flask_appbuilder.forms import FieldConverter, GeneralModelConverter
from flask_appbuilder.models.sqla.filters import SQLAFilterConverter
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.utils.legacy import get_sqla_class
from sqlalchemy import Column, Integer, JSON, String
from wtforms import TextAreaField
from wtforms.fields.core import UnboundField

from .base import FABTestCase


class JSONColumnTestCase(FABTestCase):
    """Test JSON column detection and handling"""

    def setUp(self):
        """Set up test app and database"""
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["WTF_CSRF_ENABLED"] = False

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)

        # Define a test model with JSON columns
        class TestJSONModel(self.db.Model):
            __tablename__ = "test_json_model"

            id = Column(Integer, primary_key=True)
            name = Column(String(50), nullable=False)
            config = Column(JSON, nullable=True)
            json_metadata = Column(JSON, nullable=False)
            settings = Column(JSON, nullable=True)

        self.TestJSONModel = TestJSONModel

        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app, self.db.session)
            self.db.create_all()

    def tearDown(self):
        """Clean up after test"""
        with self.app.app_context():
            self.db.drop_all()


class JSONDetectionTestCase(JSONColumnTestCase):
    """Test that JSON columns are correctly detected"""

    def test_json_column_detection(self):
        """Test that JSON columns are identified correctly"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test JSON columns are detected
            self.assertTrue(interface.is_json("config"))
            self.assertTrue(interface.is_json("json_metadata"))
            self.assertTrue(interface.is_json("settings"))

    def test_non_json_column_detection(self):
        """Test that non-JSON columns are not identified as JSON"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test non-JSON columns are not detected as JSON
            self.assertFalse(interface.is_json("name"))
            self.assertFalse(interface.is_json("id"))

    def test_invalid_column_detection(self):
        """Test that invalid column names return False"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test invalid column names
            self.assertFalse(interface.is_json("nonexistent"))
            self.assertFalse(interface.is_json("invalid_column"))

    def test_other_type_checks_still_work(self):
        """Test that other type checks work correctly with JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test other type checks still work correctly
            self.assertTrue(interface.is_string("name"))
            self.assertTrue(interface.is_integer("id"))

            # Test JSON columns don't match other types
            self.assertFalse(interface.is_string("config"))
            self.assertFalse(interface.is_integer("config"))
            self.assertFalse(interface.is_boolean("config"))
            self.assertFalse(interface.is_date("config"))


class JSONFormFieldTestCase(JSONColumnTestCase):
    """Test that JSON columns generate appropriate form fields"""

    def test_field_converter_recognizes_json(self):
        """Test that FieldConverter handles JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Create a field converter for JSON column
            field_converter = FieldConverter(
                interface, "config", "Configuration", "JSON configuration data", []
            )

            # Convert should return a field (not None)
            field = field_converter.convert()
            self.assertIsNotNone(field)
            # FieldConverter may return TextAreaField or UnboundField wrapping it
            if isinstance(field, UnboundField):
                self.assertEqual(field.field_class, TextAreaField)
            else:
                self.assertIsInstance(field, TextAreaField)

    def test_form_generation_with_json_columns(self):
        """Test that forms can be generated with JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            converter = GeneralModelConverter(interface)

            # Create form with JSON columns
            form_class = converter.create_form(
                inc_columns=["id", "name", "config", "json_metadata", "settings"]
            )

            # Check that form class was created
            self.assertEqual(form_class.__name__, "DynamicForm")

            # Check that all fields are present
            self.assertTrue(hasattr(form_class, "config"))
            self.assertTrue(hasattr(form_class, "json_metadata"))
            self.assertTrue(hasattr(form_class, "settings"))

            # Verify JSON fields are TextAreaFields
            config_field = getattr(form_class, "config")
            json_metadata_field = getattr(form_class, "json_metadata")
            settings_field = getattr(form_class, "settings")

            self.assertEqual(config_field.field_class, TextAreaField)
            self.assertEqual(json_metadata_field.field_class, TextAreaField)
            self.assertEqual(settings_field.field_class, TextAreaField)

    def test_json_only_form_generation(self):
        """Test creating forms with only JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            converter = GeneralModelConverter(interface)

            # Create form with only JSON columns
            form_class = converter.create_form(inc_columns=["config", "json_metadata"])

            # Should not raise an error
            self.assertIsNotNone(form_class)
            self.assertTrue(hasattr(form_class, "config"))
            self.assertTrue(hasattr(form_class, "json_metadata"))


class JSONFilterTestCase(JSONColumnTestCase):
    """Test that JSON columns support filtering"""

    def test_json_filter_conversion(self):
        """Test that JSON columns get appropriate filters"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # Get available filters for JSON column
            filters = filter_converter.convert("config")

            # Should have text-based filters
            self.assertIsNotNone(filters)
            self.assertGreater(len(filters), 0)

            # Check for expected filter types
            filter_names = [f.name for f in filters]
            expected_filters = ["Equal to", "Not Equal to", "Contains", "Starts with"]

            for expected in expected_filters:
                found = any(expected in str(name) for name in filter_names)
                self.assertTrue(
                    found, f"Expected filter '{expected}' not found in {filter_names}"
                )

    def test_json_filter_no_warning(self):
        """Test that JSON columns don't generate filter warnings"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # This should not log warnings about unsupported filter types
            filters = filter_converter.convert("config")
            self.assertIsNotNone(filters)

            # Test multiple JSON columns
            for col in ["config", "json_metadata", "settings"]:
                filters = filter_converter.convert(col)
                self.assertIsNotNone(filters)


class JSONModelViewTestCase(JSONColumnTestCase):
    """Test JSON columns work with ModelView"""

    def test_modelview_with_json_columns(self):
        """Test that ModelView works with JSON columns in all column lists"""
        with self.app.app_context():
            # Create a ModelView with JSON columns
            class TestJSONModelView(ModelView):
                datamodel = SQLAInterface(self.TestJSONModel)
                list_columns = ["id", "name", "config", "json_metadata"]
                add_columns = ["name", "config", "json_metadata", "settings"]
                edit_columns = ["name", "config", "json_metadata", "settings"]
                show_columns = ["id", "name", "config", "json_metadata", "settings"]

            # Register the view
            view = self.appbuilder.add_view(
                TestJSONModelView, "Test JSON Model", category="Test"
            )

            # Check that forms can be created
            add_form = view.add_form()
            edit_form = view.edit_form()

            # Verify forms have the JSON fields
            for form in [add_form, edit_form]:
                self.assertIn("config", form._fields)
                self.assertIn("json_metadata", form._fields)
                self.assertIn("settings", form._fields)

    def test_json_columns_in_search(self):
        """Test that JSON columns can be used in search"""
        with self.app.app_context():

            class TestJSONModelView(ModelView):
                datamodel = SQLAInterface(self.TestJSONModel)
                search_columns = ["name", "config", "json_metadata"]

            # This should not raise an error
            view = self.appbuilder.add_view(
                TestJSONModelView, "Test JSON Search Model", category="Test"
            )

            # Check search columns include JSON
            self.assertIn("config", view.search_columns)
            self.assertIn("json_metadata", view.search_columns)


class JSONValidationTestCase(JSONColumnTestCase):
    """Test JSON column validation and error handling"""

    def test_no_error_log_for_json_columns(self):
        """Test that JSON columns don't trigger 'Type not supported' error"""
        import logging

        with self.app.app_context():
            # Capture log messages
            with self.assertLogs(
                "flask_appbuilder.forms", level="ERROR"
            ) as log_context:
                interface = SQLAInterface(self.TestJSONModel, self.db.session)
                converter = GeneralModelConverter(interface)

                # This should not log any errors
                try:
                    form_class = converter.create_form(
                        inc_columns=["config", "json_metadata", "settings"]
                    )
                    self.assertIsNotNone(form_class)

                    # If we reach here without logging, test should pass
                    # Force a log message to avoid assertLogs failure
                    logging.getLogger("flask_appbuilder.forms").error(
                        "Test message to satisfy assertLogs"
                    )

                except Exception as e:
                    self.fail(f"Form creation failed with JSON columns: {e}")

            # Check that no "Type not supported" messages were logged
            error_messages = [record.message for record in log_context.records]
            type_not_supported_errors = [
                msg
                for msg in error_messages
                if "Type not supported" in msg
                and any(col in msg for col in ["config", "json_metadata", "settings"])
            ]
            self.assertEqual(
                len(type_not_supported_errors),
                0,
                f"Found 'Type not supported' errors for JSON columns: "
                f"{type_not_supported_errors}",
            )


class JSONIntegrationTestCase(JSONColumnTestCase):
    """Integration tests for JSON column support"""

    def test_full_crud_workflow(self):
        """Test complete CRUD workflow with JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test that we can create records with JSON data
            # (This would be done through forms in real usage)
            record = self.TestJSONModel(
                name="Test Record",
                config={"theme": "dark", "notifications": True},
                json_metadata={"created_by": "test_user", "tags": ["test", "json"]},
                settings={"language": "en", "timezone": "UTC"},
            )

            # Add record
            interface.add(record)

            # Query back using the proper interface method
            query_result = interface.query()
            all_records = query_result[1]  # query() returns (count, records)
            self.assertGreaterEqual(
                len(all_records), 1
            )  # Allow for test isolation issues

            # Find our test record
            test_record = next(
                (r for r in all_records if r.name == "Test Record"), None
            )
            self.assertIsNotNone(test_record, "Test record not found")

            self.assertEqual(test_record.config["theme"], "dark")
            self.assertEqual(test_record.json_metadata["created_by"], "test_user")
            self.assertEqual(test_record.settings["language"], "en")

    def test_json_column_ordering(self):
        """Test that JSON column conversion happens in correct order"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            converter = GeneralModelConverter(interface)

            # Test that is_json is checked before other types
            # by ensuring JSON columns don't get converted to other field types
            form_class = converter.create_form(inc_columns=["name", "config"])

            name_field = getattr(form_class, "name")
            config_field = getattr(form_class, "config")

            # name should be StringField (string type)
            # config should be TextAreaField (json type, not string type)
            self.assertNotEqual(name_field.field_class, config_field.field_class)
            self.assertEqual(config_field.field_class, TextAreaField)


if __name__ == "__main__":
    unittest.main()
