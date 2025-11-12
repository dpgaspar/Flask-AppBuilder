"""
Additional tests to fix code coverage for JSON column support
"""

import unittest

# Mock imports removed as they're not needed
from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.models.base import BaseInterface
from flask_appbuilder.models.sqla.filters import set_value_to_type, SQLAFilterConverter
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.utils.legacy import get_sqla_class
from sqlalchemy import Column, Integer, JSON, String


class JSONCoverageFixTestCase(unittest.TestCase):
    """Test cases specifically to improve code coverage for JSON support"""

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
            __tablename__ = "test_coverage_model"

            id = Column(Integer, primary_key=True)
            name = Column(String(50), nullable=False)
            json_data = Column(JSON, nullable=True)

        self.TestJSONModel = TestJSONModel

        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app, self.db.session)
            self.db.create_all()


class BaseInterfaceJSONCoverageTestCase(JSONCoverageFixTestCase):
    """Test base interface JSON method for coverage"""

    def test_base_interface_is_json_returns_false(self):
        """Test that BaseInterface.is_json always returns False"""
        # This tests the line added to flask_appbuilder/models/base.py
        base_interface = BaseInterface(None)

        # Should always return False regardless of column name
        self.assertFalse(base_interface.is_json("any_column"))
        self.assertFalse(base_interface.is_json("json_column"))
        self.assertFalse(base_interface.is_json(""))
        self.assertFalse(base_interface.is_json(None))


class SQLAInterfaceJSONExceptionCoverageTestCase(JSONCoverageFixTestCase):
    """Test SQLAInterface JSON exception handling for coverage"""

    def test_is_json_keyerror_handling(self):
        """Test KeyError handling in SQLAInterface.is_json"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test with non-existent column - should catch KeyError and return False
            # Tests except KeyError block in flask_appbuilder/models/sqla/interface.py
            self.assertFalse(interface.is_json("nonexistent_column"))
            self.assertFalse(interface.is_json("fake_column"))
            self.assertFalse(interface.is_json(""))


class SQLAFiltersJSONCoverageTestCase(JSONCoverageFixTestCase):
    """Test SQLAlchemy filters JSON handling for coverage"""

    def test_set_value_to_type_json_conversion(self):
        """Test set_value_to_type with JSON columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test the new JSON handling code in set_value_to_type
            # This tests the lines added to flask_appbuilder/models/sqla/filters.py

            # Test with various input types for JSON column
            self.assertEqual(
                set_value_to_type(interface, "json_data", {"key": "value"}),
                "{'key': 'value'}",
            )
            self.assertEqual(set_value_to_type(interface, "json_data", 123), "123")
            self.assertEqual(set_value_to_type(interface, "json_data", True), "True")
            self.assertEqual(set_value_to_type(interface, "json_data", None), "None")
            self.assertEqual(
                set_value_to_type(interface, "json_data", "string"), "string"
            )

            # Test with non-JSON column (should not use JSON path)
            self.assertEqual(set_value_to_type(interface, "name", "test"), "test")

    def test_json_filter_converter_coverage(self):
        """Test JSON filter converter for coverage"""
        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # Test JSON column filter conversion - tests the filter conversion table
            json_filters = filter_converter.convert("json_data")

            # Should have filters available
            self.assertIsNotNone(json_filters)
            self.assertGreater(len(json_filters), 0)

            # Should include the specific filters we defined for JSON columns
            filter_names = [str(f.name) for f in json_filters]
            expected_filters = ["Equal", "Not Equal", "Contains", "Starts with"]

            for expected in expected_filters:
                found = any(expected in name for name in filter_names)
                self.assertTrue(found, f"Expected filter type '{expected}' not found")


class JSONFormsCoverageTestCase(JSONCoverageFixTestCase):
    """Test forms JSON support for coverage"""

    def test_forms_json_conversion_table_coverage(self):
        """Test that JSON appears in the forms conversion table"""
        from flask_appbuilder.forms import FieldConverter

        with self.app.app_context():
            interface = SQLAInterface(self.TestJSONModel, self.db.session)

            # Test that the conversion table includes is_json
            converter = FieldConverter(
                interface, "json_data", "JSON Data", "Test JSON field", []
            )

            # This should use the JSON conversion path in the conversion table
            field = converter.convert()
            self.assertIsNotNone(field)

            # Should be a TextAreaField (or UnboundField wrapping it)
            field_name = field.__class__.__name__
            if field_name == "UnboundField":
                # Check the wrapped field class
                self.assertEqual(field.field_class.__name__, "TextAreaField")
            else:
                self.assertIn("TextArea", field_name)


if __name__ == "__main__":
    unittest.main()
