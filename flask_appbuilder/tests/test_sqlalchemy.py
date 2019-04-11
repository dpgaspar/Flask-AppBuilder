import unittest

from flask_appbuilder.models.sqla.interface import _is_sqla_type
from nose.tools import eq_
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
        eq_(True, _is_sqla_type(t1, sa.types.DateTime))
        eq_(True, _is_sqla_type(t2, sa.types.DateTime))
        eq_(False, _is_sqla_type(t3, sa.types.DateTime))
