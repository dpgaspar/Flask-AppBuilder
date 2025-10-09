"""
Edge case tests for JSON column support in Flask-AppBuilder
"""

import unittest

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.forms import FieldConverter
from flask_appbuilder.models.sqla.filters import set_value_to_type, SQLAFilterConverter
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.utils.legacy import get_sqla_class
from sqlalchemy import Boolean, Column, Integer, JSON, String, Text
from wtforms import TextAreaField
from wtforms.fields.core import UnboundField

from .base import FABTestCase


class JSONEdgeCaseTestCase(FABTestCase):
    """Test edge cases and error conditions for JSON support"""

    def setUp(self):
        """Set up test app and database"""
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)

        # Define models with various column types including JSON
        class MixedTypeModel(self.db.Model):
            __tablename__ = "mixed_type_model"

            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            description = Column(Text)
            is_active = Column(Boolean)
            json_data = Column(JSON)
            json_nullable = Column(JSON, nullable=True)
            json_not_null = Column(JSON, nullable=False)

        self.MixedTypeModel = MixedTypeModel

        with self.app.app_context():
            self.appbuilder = AppBuilder(self.app, self.db.session)
            self.db.create_all()

    def tearDown(self):
        """Clean up after test"""
        with self.app.app_context():
            self.db.drop_all()


class JSONTypeDetectionEdgeCasesTestCase(JSONEdgeCaseTestCase):
    """Test edge cases in JSON type detection"""

    def test_json_vs_text_distinction(self):
        """Test that JSON columns are distinguished from Text columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # JSON column should be detected as JSON, not text
            self.assertTrue(interface.is_json("json_data"))
            self.assertFalse(interface.is_text("json_data"))

            # Text column should be detected as text, not JSON
            self.assertTrue(interface.is_text("description"))
            self.assertFalse(interface.is_json("description"))

    def test_json_vs_string_distinction(self):
        """Test that JSON columns are distinguished from String columns"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # JSON column should be detected as JSON, not string
            self.assertTrue(interface.is_json("json_data"))
            self.assertFalse(interface.is_string("json_data"))

            # String column should be detected as string, not JSON
            self.assertTrue(interface.is_string("name"))
            self.assertFalse(interface.is_json("name"))

    def test_json_nullable_vs_not_null(self):
        """Test that both nullable and non-nullable JSON columns are detected"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # Both nullable and non-nullable JSON columns should be detected
            self.assertTrue(interface.is_json("json_nullable"))
            self.assertTrue(interface.is_json("json_not_null"))

            # Check nullability is handled correctly
            self.assertTrue(interface.is_nullable("json_nullable"))
            self.assertFalse(interface.is_nullable("json_not_null"))


class JSONFormFieldEdgeCasesTestCase(JSONEdgeCaseTestCase):
    """Test edge cases in JSON form field generation"""

    def test_field_converter_ordering(self):
        """Test that JSON check happens before other type checks in FieldConverter"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # Create field converters for different types
            json_converter = FieldConverter(
                interface, "json_data", "JSON Data", "JSON field", []
            )
            text_converter = FieldConverter(
                interface, "description", "Description", "Text field", []
            )

            # Convert fields
            json_field = json_converter.convert()
            text_field = text_converter.convert()

            # Both should be TextAreaField but for different reasons
            # Check field types (may be UnboundField)
            if isinstance(json_field, UnboundField):
                self.assertEqual(json_field.field_class, TextAreaField)
            else:
                self.assertIsInstance(json_field, TextAreaField)

            if isinstance(text_field, UnboundField):
                self.assertEqual(text_field.field_class, TextAreaField)
            else:
                self.assertIsInstance(text_field, TextAreaField)

            # Verify the conversion table order works correctly
            # (JSON should be checked before text/string)
            self.assertTrue(interface.is_json("json_data"))
            self.assertFalse(interface.is_text("json_data"))  # Should not match text
            self.assertFalse(
                interface.is_string("json_data")
            )  # Should not match string

    def test_no_error_on_json_conversion(self):
        """Test that JSON field conversion doesn't log errors"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            converter = FieldConverter(
                interface, "json_data", "JSON Data", "JSON configuration", []
            )

            # This should not return None (which would indicate an error)
            field = converter.convert()
            self.assertIsNotNone(field)
            # Check field type (may be UnboundField)
            if isinstance(field, UnboundField):
                self.assertEqual(field.field_class, TextAreaField)
            else:
                self.assertIsInstance(field, TextAreaField)


class JSONFilterEdgeCasesTestCase(JSONEdgeCaseTestCase):
    """Test edge cases in JSON filtering"""

    def test_json_filter_value_conversion(self):
        """Test that JSON values are properly converted for filtering"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # Test set_value_to_type function with JSON columns
            test_values = [
                ('{"key": "value"}', '{"key": "value"}'),  # JSON string
                (123, "123"),  # Number to string
                (True, "True"),  # Boolean to string
                ("simple text", "simple text"),  # Plain string
            ]

            for input_value, expected in test_values:
                result = set_value_to_type(interface, "json_data", input_value)
                self.assertEqual(result, expected)

    def test_json_filter_availability(self):
        """Test that JSON columns have appropriate filters available"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # Get filters for JSON column
            json_filters = filter_converter.convert("json_data")

            # Should have filters available
            self.assertIsNotNone(json_filters)
            self.assertGreater(len(json_filters), 0)

            # Should have text-based filters (not numeric filters)
            filter_names = [str(f.name) for f in json_filters]

            # Should have text filters
            self.assertTrue(any("Contains" in name for name in filter_names))
            self.assertTrue(any("Equal" in name for name in filter_names))

            # Should not have numeric filters
            self.assertFalse(any("Greater" in name for name in filter_names))
            self.assertFalse(any("Smaller" in name for name in filter_names))

    def test_non_json_columns_unaffected(self):
        """Test that non-JSON columns still get their appropriate filters"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # Integer column should get numeric filters
            int_filters = filter_converter.convert("id")
            int_filter_names = [str(f.name) for f in int_filters]
            self.assertTrue(any("Greater" in name for name in int_filter_names))

            # Boolean column should get boolean filters
            bool_filters = filter_converter.convert("is_active")
            bool_filter_names = [str(f.name) for f in bool_filters]
            self.assertTrue(any("Equal" in name for name in bool_filter_names))

            # String column should get string filters
            str_filters = filter_converter.convert("name")
            str_filter_names = [str(f.name) for f in str_filters]
            self.assertTrue(any("Contains" in name for name in str_filter_names))


class JSONErrorHandlingTestCase(JSONEdgeCaseTestCase):
    """Test error handling and robustness"""

    def test_invalid_column_name_handling(self):
        """Test that invalid column names are handled gracefully"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # Should not raise exceptions for invalid column names
            self.assertFalse(interface.is_json("nonexistent_column"))
            self.assertFalse(interface.is_json(""))
            self.assertFalse(interface.is_json(None))

    def test_filter_converter_robustness(self):
        """Test that filter converter handles edge cases gracefully"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)
            filter_converter = SQLAFilterConverter(interface)

            # Should handle invalid column names gracefully
            result = filter_converter.convert("nonexistent_column")
            # Should return None or empty list, not raise exception
            self.assertTrue(result is None or len(result) == 0)

    def test_set_value_to_type_robustness(self):
        """Test that set_value_to_type handles edge cases"""
        with self.app.app_context():
            interface = SQLAInterface(self.MixedTypeModel, self.db.session)

            # Test with None value
            result = set_value_to_type(interface, "json_data", None)
            self.assertEqual(result, "None")

            # Test with empty string
            result = set_value_to_type(interface, "json_data", "")
            self.assertEqual(result, "")

            # Test with invalid column name (should return value unchanged)
            test_value = "test"
            result = set_value_to_type(interface, "nonexistent", test_value)
            self.assertEqual(result, test_value)


if __name__ == "__main__":
    unittest.main()
