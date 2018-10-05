from nose.tools import eq_
import unittest
import sqlalchemy as sa
from flask_appbuilder.models.sqla.interface import _is_sqla_type
from flask_appbuilder.models.sqla.interface import SQLAInterface

Base = sa.ext.declarative.declarative_base()


class Parent(Base):
    __tablename__ = 'parent'
    id = sa.Column(sa.Integer, primary_key=True)
    favorite_child = sa.orm.relation('FavoriteChild', back_populates='parent',
                                     uselist=False)
    children = sa.orm.relation('Child', back_populates='parent')


class FavoriteChild(Base):
    __tablename__ = 'favorite_child'
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = sa.orm.relation(Parent, back_populates='favorite_child')


class Child(Base):
    __tablename__ = 'child'
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = sa.orm.relation(Parent, back_populates='children')


class CustomSqlaType(sa.types.TypeDecorator):
    impl = sa.types.DateTime(timezone=True)


class NotSqlaType():
    def __init__(self):
        self.impl = sa.types.DateTime(timezone=True)


class FlaskTestCase(unittest.TestCase):
    def test_is_one_to_one(self):
        interf = SQLAInterface(Parent)
        eq_(True,  interf.is_relation_one_to_one('favorite_child'))
        eq_(False,  interf.is_relation_one_to_many('favorite_child'))

    def test_is_one_to_many(self):
        interf = SQLAInterface(Parent)
        eq_(True,  interf.is_relation_one_to_many('children'))
        eq_(False,  interf.is_relation_one_to_one('children'))

    def test_is_sqla_type(self):
        t1 = sa.types.DateTime(timezone=True)
        t2 = CustomSqlaType()
        t3 = NotSqlaType()
        eq_(True, _is_sqla_type(t1, sa.types.DateTime))
        eq_(True, _is_sqla_type(t2, sa.types.DateTime))
        eq_(False, _is_sqla_type(t3, sa.types.DateTime))
