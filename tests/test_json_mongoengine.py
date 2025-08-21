"""
Tests for JSON column support in Flask-AppBuilder with MongoEngine
"""

import unittest
import sys

try:
    import mongoengine
    from mongoengine import Document, StringField, IntField, DictField
    from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
    from flask_appbuilder.models.mongoengine.filters import MongoEngineFilterConverter
    HAS_MONGOENGINE = True
except ImportError:
    HAS_MONGOENGINE = False


@unittest.skipIf(not HAS_MONGOENGINE, "MongoEngine not available")
class MongoEngineJSONTestCase(unittest.TestCase):
    """Test JSON (DictField) support in MongoEngine interface"""
    
    def setUp(self):
        """Set up test document"""
        # Define a test document with DictField (JSON equivalent)
        class TestDocument(Document):
            name = StringField(max_length=50, required=True)
            age = IntField()
            config = DictField()  # This should be detected as JSON
            metadata = DictField(required=True)
            settings = DictField()
            
            meta = {'collection': 'test_json_docs'}
        
        self.TestDocument = TestDocument
    
    def test_dictfield_json_detection(self):
        """Test that DictField columns are detected as JSON"""
        interface = MongoEngineInterface(self.TestDocument)
        
        # Test DictField columns are detected as JSON
        self.assertTrue(interface.is_json('config'))
        self.assertTrue(interface.is_json('metadata'))
        self.assertTrue(interface.is_json('settings'))
    
    def test_non_dictfield_not_json(self):
        """Test that non-DictField columns are not detected as JSON"""
        interface = MongoEngineInterface(self.TestDocument)
        
        # Test non-DictField columns are not detected as JSON
        self.assertFalse(interface.is_json('name'))
        self.assertFalse(interface.is_json('age'))
    
    def test_invalid_column_returns_false(self):
        """Test that invalid column names return False for JSON detection"""
        interface = MongoEngineInterface(self.TestDocument)
        
        # Test invalid column names
        self.assertFalse(interface.is_json('nonexistent'))
        self.assertFalse(interface.is_json('invalid_field'))
    
    def test_other_type_checks_work(self):
        """Test that other type checks still work with DictField present"""
        interface = MongoEngineInterface(self.TestDocument)
        
        # Test other type checks still work
        self.assertTrue(interface.is_string('name'))
        self.assertTrue(interface.is_integer('age'))
        
        # Test DictField doesn't match other types
        self.assertFalse(interface.is_string('config'))
        self.assertFalse(interface.is_integer('config'))
        self.assertFalse(interface.is_boolean('config'))
    
    def test_json_filter_support(self):
        """Test that DictField columns support filtering"""
        interface = MongoEngineInterface(self.TestDocument)
        filter_converter = MongoEngineFilterConverter(interface)
        
        # Get available filters for DictField column
        filters = filter_converter.convert('config')
        
        # Should have text-based filters
        self.assertIsNotNone(filters)
        self.assertGreater(len(filters), 0)
        
        # Check for expected filter types
        filter_names = [f.name for f in filters]
        expected_filters = ['Equal to', 'Not Equal to', 'Contains', 'Starts with']
        
        for expected in expected_filters:
            found = any(expected in str(name) for name in filter_names)
            self.assertTrue(found, f"Expected filter '{expected}' not found in {filter_names}")
    
    def test_multiple_dictfield_filters(self):
        """Test that multiple DictField columns can be filtered"""
        interface = MongoEngineInterface(self.TestDocument)
        filter_converter = MongoEngineFilterConverter(interface)
        
        # Test multiple DictField columns
        for col in ['config', 'metadata', 'settings']:
            filters = filter_converter.convert(col)
            self.assertIsNotNone(filters, f"No filters found for DictField column: {col}")
            self.assertGreater(len(filters), 0, f"No filters available for DictField column: {col}")


@unittest.skipIf(not HAS_MONGOENGINE, "MongoEngine not available")  
class MongoEngineJSONIntegrationTestCase(unittest.TestCase):
    """Integration tests for MongoEngine JSON support"""
    
    def setUp(self):
        """Set up test document for integration tests"""
        class IntegrationDocument(Document):
            name = StringField(required=True)
            user_preferences = DictField()
            app_config = DictField(required=True)
            
            meta = {'collection': 'integration_test_docs'}
        
        self.IntegrationDocument = IntegrationDocument
    
    def test_interface_creation(self):
        """Test that interface can be created with DictField columns"""
        # Should not raise any exceptions
        interface = MongoEngineInterface(self.IntegrationDocument)
        self.assertIsNotNone(interface)
        
        # Check that DictField columns are properly handled
        self.assertTrue(interface.is_json('user_preferences'))
        self.assertTrue(interface.is_json('app_config'))
    
    def test_form_field_generation_compatibility(self):
        """Test that DictField columns would work with form generation"""
        interface = MongoEngineInterface(self.IntegrationDocument)
        
        # Check that the interface methods needed for form generation work
        self.assertTrue(hasattr(interface, 'is_json'))
        self.assertTrue(callable(interface.is_json))
        
        # Verify the is_json method works correctly
        self.assertTrue(interface.is_json('user_preferences'))
        self.assertFalse(interface.is_json('name'))


if __name__ == '__main__':
    if HAS_MONGOENGINE:
        unittest.main()
    else:
        print("Skipping MongoEngine JSON tests - MongoEngine not available")
        sys.exit(0)