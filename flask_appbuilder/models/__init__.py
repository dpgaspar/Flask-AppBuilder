import logging
import re
from functools import partial
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.event import listen
from sqlalchemy import create_engine


log = logging.getLogger(__name__)

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class BackEnd(object):

    engine = None
    engines = None

    def __init__(self, app):
        self.app = app
        self.init_engines()
        self.session = self.create_scoped_session()
        teardown = app.teardown_appcontext

        @teardown
        def shutdown_session(response_or_exc):
            self.session.remove()
            return response_or_exc

    def init_engines(self):
        self.engines = {}
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])
        binds = self.app.config['SQLALCHEMY_BINDS']
        for bind in binds:
            self.engines[bind] = create_engine(binds[bind])


    def create_all(self):
        tables = self.get_tables_for_bind_key()
        Model.metadata.create_all(self.engine, tables)
        for key in self.engines:
            tables = self.get_tables_for_bind_key(key)
            Model.metadata.create_all(self.engines[key], tables)

    @staticmethod
    def get_tables_for_bind_key(bind_key=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        tables = Model.metadata.tables
        for table in tables:
            table_class = tables[table]
            if table_class.info.get('bind_key') == bind_key:
                result.append(table_class)
        return result

    def create_scoped_session(self):
        """Helper factory method that creates a scoped session.  It
        internally calls :meth:`create_session`.
        """
        return scoped_session(partial(self.create_session))

    def create_session(self):
        return RoutingSession(self)


class _EngineDebuggingSignalEvents(object):
    """Sets up handlers for two events that let us track the execution time of queries."""

    def __init__(self, engine, import_name):
        self.engine = engine
        self.app_package = import_name

    def register(self):
        listen(self.engine, 'before_cursor_execute', self.before_cursor_execute)
        listen(self.engine, 'after_cursor_execute', self.after_cursor_execute)

    def before_cursor_execute(self, conn, cursor, statement,
                              parameters, context, executemany):
        pass

    def after_cursor_execute(self, conn, cursor, statement,
                              parameters, context, executemany):
        pass

class RoutingSession(Session):
    """
        Routes Sessions to the correct engines, support multiple dbs.
    """
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.db = db
        Session.__init__(self, autocommit=autocommit, autoflush=autoflush,
                         bind=self.db.engine, **options)

    def get_bind(self, mapper=None, clause=None):
        if mapper:
            if hasattr(mapper.class_, '__bind_key__'):
                return self.db.engines[mapper.class_.__bind_key__]
            return self.db.engine
        return self.db.engine


class ModelDeclarativeMeta(DeclarativeMeta):
    """
        Base Model declarative meta for all Models definitions.
        Setups bind_keys to support multiple databases.
        Setup the table name based on the class camelcase name.
    """
    def __new__(cls, name, bases, d):
        tablename = d.get('__tablename__')
        if not tablename and d.get('__table__') is None:
            d['__tablename__'] = _camelcase_re.sub(cls._join, name).lstrip('_')
        return DeclarativeMeta.__new__(cls, name, bases, d)

    def __init__(self, name, bases, d):
        bind_key = d.pop('__bind_key__', None)
        DeclarativeMeta.__init__(self, name, bases, d)
        if bind_key is not None:
            self.__table__.info['bind_key'] = bind_key

    @staticmethod
    def _join(match):
        word = match.group()
        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()
        return '_' + word.lower()


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

