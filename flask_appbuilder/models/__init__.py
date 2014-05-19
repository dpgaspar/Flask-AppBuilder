import logging
import re
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy, _BoundDeclarativeMeta, _QueryProperty

log = logging.getLogger(__name__)

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class SQLA(SQLAlchemy):
    """
        This is a child class of flask.ext.SQLAlchemy
        It's propose is to override the declarative base of the original
        package. So that it is bound to F.A.B. Model class allowing the dev
        to be in the same namespace of the security tables (and others)
        and can use AuditMixin class alike.

        Use it and configure it just like flask.ext.SQLAlchemy
    """
    def make_declarative_base(self):
        """Creates the declarative base."""
        base = declarative_base(cls=Model, name='Model',
                                metaclass=ModelDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        tables = Model.metadata.tables
        for key in tables:
            if tables[key].info.get('bind_key') == bind:
                result.append(tables[key])
        return result



class ModelDeclarativeMeta(_BoundDeclarativeMeta):
    """
        Base Model declarative meta for all Models definitions.
        Setups bind_keys to support multiple databases.
        Setup the table name based on the class camelcase name.
    """


@as_declarative(name='Model', metaclass=ModelDeclarativeMeta)
class Model(object):
    """
        Use this class has the base for your models, it will define your table names automatically
        MyModel will be called my_model on the database.

        ::

            from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, Date
            from flask.ext.appbuilder import Model

            class MyModel(Model):
                id = Column(Integer, primary_key=True)
                name = Column(String(50), unique = True, nullable=False)

    """
    __table_args__ = {'extend_existing': True}


"""
    This is for retro compatibility
"""
Base = Model

