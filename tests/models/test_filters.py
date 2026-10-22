import datetime
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.models.sqla.filters import (
    FilterEndsWith,
    FilterGreater,
    FilterIn,
    FilterInFunction,
    FilterNotContains,
    FilterNotEndsWith,
    FilterNotEqual,
    FilterNotIn,
    FilterNotStartsWith,
    FilterSmaller,
    set_value_to_type,
)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.utils.legacy import get_sqla_class
from tests.sqla.models import Model1


class SetValueToTypeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")
        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.datamodel = SQLAInterface(Model1, self.db.session)

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_integer_conversion(self):
        result = set_value_to_type(self.datamodel, "field_integer", "42")
        self.assertEqual(result, 42)

    def test_integer_conversion_failure(self):
        result = set_value_to_type(self.datamodel, "field_integer", "not_a_number")
        self.assertIsNone(result)

    def test_float_conversion(self):
        result = set_value_to_type(self.datamodel, "field_float", "3.14")
        self.assertAlmostEqual(result, 3.14)

    def test_float_conversion_failure(self):
        result = set_value_to_type(self.datamodel, "field_float", "not_a_float")
        self.assertIsNone(result)

    def test_date_conversion(self):
        result = set_value_to_type(self.datamodel, "field_date", "2024-01-15")
        self.assertEqual(result, datetime.date(2024, 1, 15))

    def test_date_passthrough_when_already_date(self):
        d = datetime.date(2024, 1, 15)
        result = set_value_to_type(self.datamodel, "field_date", d)
        self.assertEqual(result, d)

    def test_date_conversion_failure(self):
        result = set_value_to_type(self.datamodel, "field_date", "not_a_date")
        self.assertIsNone(result)

    def test_string_passthrough(self):
        result = set_value_to_type(self.datamodel, "field_string", "hello")
        self.assertEqual(result, "hello")


class FilterApplyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.datamodel = SQLAInterface(Model1, self.db.session)

        for i in range(5):
            self.db.session.add(
                Model1(
                    field_string=f"test{i}",
                    field_integer=i * 10,
                    field_float=float(i),
                    field_date=datetime.date(2024, 1, i + 1),
                )
            )
        self.db.session.commit()

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def _base_query(self):
        return self.db.session.query(Model1)

    def test_filter_not_starts_with(self):
        f = FilterNotStartsWith("field_string", self.datamodel)
        q = f.apply(self._base_query(), "test0")
        self.assertEqual(q.count(), 4)

    def test_filter_ends_with(self):
        f = FilterEndsWith("field_string", self.datamodel)
        q = f.apply(self._base_query(), "t1")
        self.assertEqual(q.count(), 1)

    def test_filter_not_ends_with(self):
        f = FilterNotEndsWith("field_string", self.datamodel)
        q = f.apply(self._base_query(), "t1")
        self.assertEqual(q.count(), 4)

    def test_filter_not_contains(self):
        f = FilterNotContains("field_string", self.datamodel)
        q = f.apply(self._base_query(), "st0")
        self.assertEqual(q.count(), 4)

    def test_filter_not_equal(self):
        f = FilterNotEqual("field_integer", self.datamodel)
        q = f.apply(self._base_query(), "10")
        self.assertEqual(q.count(), 4)

    def test_filter_greater(self):
        f = FilterGreater("field_integer", self.datamodel)
        q = f.apply(self._base_query(), "20")
        self.assertEqual(q.count(), 2)

    def test_filter_greater_unparseable_returns_unfiltered(self):
        f = FilterGreater("field_integer", self.datamodel)
        q = f.apply(self._base_query(), "not_a_number")
        self.assertEqual(q.count(), 5)

    def test_filter_smaller(self):
        f = FilterSmaller("field_integer", self.datamodel)
        q = f.apply(self._base_query(), "20")
        self.assertEqual(q.count(), 2)

    def test_filter_smaller_unparseable_returns_unfiltered(self):
        f = FilterSmaller("field_integer", self.datamodel)
        q = f.apply(self._base_query(), "not_a_number")
        self.assertEqual(q.count(), 5)

    def test_filter_in(self):
        f = FilterIn("field_integer", self.datamodel)
        q = f.apply(self._base_query(), ["10", "20"])
        self.assertEqual(q.count(), 2)

    def test_filter_not_in(self):
        f = FilterNotIn("field_integer", self.datamodel)
        q = f.apply(self._base_query(), ["10", "20"])
        self.assertEqual(q.count(), 3)

    def test_filter_in_function(self):
        f = FilterInFunction("field_integer", self.datamodel)
        q = f.apply(self._base_query(), lambda: [0, 10])
        self.assertEqual(q.count(), 2)


if __name__ == "__main__":
    unittest.main()
