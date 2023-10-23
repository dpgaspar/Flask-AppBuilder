import datetime
import logging
import re

from flask_sqlalchemy import (
    _QueryProperty,
    DefaultMeta,
    get_state,
    SessionBase,
    SignallingSession,
    SQLAlchemy,
)
from sqlalchemy import orm

try:
    from sqlalchemy.ext.declarative import as_declarative
except ImportError:
    from sqlalchemy.ext.declarative.api import as_declarative

try:
    from sqlalchemy.orm.util import identity_key  # noqa

    has_identity_key = True
except ImportError:
    has_identity_key = False

log = logging.getLogger(__name__)

_camelcase_re = re.compile(r"([A-Z]+)(?=[a-z0-9])")


class CustomSignallingSession(SignallingSession):
    """
    Custom Signaling Session to support SQLALchemy>=1.4 with flask-sqlalchemy 2.X
    https://github.com/pallets/flask-sqlalchemy/issues/953
    """

    def get_bind(self, mapper=None, *args, **kwargs):
        """Return the engine or connection for a given model or
        table, using the ``__bind_key__`` if it is set.

        Patch from https://github.com/pallets/flask-sqlalchemy/pull/1001
        """
        # mapper is None if someone tries to just get a connection
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table
            info = getattr(persist_selectable, "info", {})
            bind_key = info.get("bind_key")
            if bind_key is not None:
                state = get_state(self.app)
                return state.db.get_engine(self.app, bind=bind_key)
        return SessionBase.get_bind(self, mapper, *args, **kwargs)


class SQLA(SQLAlchemy):
    """
    This is a child class of flask_SQLAlchemy
    It's purpose is to override the declarative base of the original
    package. So that it is bound to F.A.B. Model class allowing the dev
    to be in the same namespace of the security tables (and others)
    and can use AuditMixin class alike.

    Use it and configure it just like flask_SQLAlchemy
    """

    def make_declarative_base(self, model, metadata=None):
        base = Model
        base.query = _QueryProperty(self)
        return base

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        tables = Model.metadata.tables
        for key in tables:
            if tables[key].info.get("bind_key") == bind:
                result.append(tables[key])
        return result

    def create_session(self, options):
        """
        Custom Session factory to support SQLALchemy>=1.4 with flask-sqlalchemy 2.X

        https://github.com/pallets/flask-sqlalchemy/issues/953

        :param options: dict of keyword arguments passed to session class
        """

        return orm.sessionmaker(class_=CustomSignallingSession, db=self, **options)


class ModelDeclarativeMeta(DefaultMeta):
    """
    Base Model declarative meta for all Models definitions.
    Setups bind_keys to support multiple databases.
    Setup the table name based on the class camelcase name.
    """


@as_declarative(name="Model", metaclass=ModelDeclarativeMeta)
class Model(object):
    """
    Use this class has the base for your models,
    it will define your table names automatically
    MyModel will be called my_model on the database.

    ::

        from sqlalchemy import Integer, String
        from flask_appbuilder import Model

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

    """

    __table_args__ = {"extend_existing": True}

    def to_json(self):
        result = dict()
        for key in self.__mapper__.c.keys():
            col = getattr(self, key)
            if isinstance(col, datetime.datetime) or isinstance(col, datetime.date):
                col = col.isoformat()
            result[key] = col
        return result


"""
    This is for retro compatibility
"""
Base = Model
