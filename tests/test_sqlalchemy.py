import unittest

from flask_appbuilder.models.sqla.interface import _is_sqla_type
import sqlalchemy as sa


class CustomSqlaType(sa.types.TypeDecorator):
    impl = sa.types.DateTime(timezone=True)


class NotSqlaType:
    def __init__(self):
        self.impl = sa.types.DateTime(timezone=True)


class FlaskTestCase(unittest.TestCase):
    def test_is_sqla_type(self):
        t1 = sa.types.DateTime(timezone=True)
        t2 = CustomSqlaType()
        t3 = NotSqlaType()
        self.assertTrue(_is_sqla_type(t1, sa.types.DateTime))
        self.assertTrue(_is_sqla_type(t2, sa.types.DateTime))
        self.assertFalse(_is_sqla_type(t3, sa.types.DateTime))
