import logging
import re
from functools import partial
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
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
        log.debug("CREATE DB {0}".format(self.engine, tables))
        Model.metadata.create_all(self.engine, tables)
        for key in self.engines:
            tables = self.get_tables_for_bind_key(key)
            log.debug("CREATE DB {0} TABLES: {1}".format(self.engines[key], tables))
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


class RoutingSession(Session):
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.db = db
        Session.__init__(self, autocommit=autocommit, autoflush=autoflush,
                         bind=self.db.engine, **options)

    def get_bind(self, mapper=None, clause=None):
        if mapper:
            #log.info("Get BIND MAPPER {0} {1}".format(mapper, mapper.class_))
            if hasattr(mapper.class_, '__bind_key__'):
                log.info("ALTER BIND {0}".format(mapper.class_.__bind_key__))
                return self.db.engines[mapper.class_.__bind_key__]
            return self.db.engine
        return self.db.engine


class ModelDeclarativeMeta(DeclarativeMeta):

    def __init__(self, name, bases, d):
        bind_key = d.pop('__bind_key__', None)
        DeclarativeMeta.__init__(self, name, bases, d)
        if bind_key is not None:
            self.__table__.info['bind_key'] = bind_key


@as_declarative(name='Model', metaclass=ModelDeclarativeMeta)
class Model(object):
    """
        Use this class has the base for your models, it will define your tablenames automatically
        MyModel will be called my_model on the database.

        ::

            from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, Date
            from flask.ext.appbuilder import Model

            class MyModel(Model):
                id = Column(Integer, primary_key=True)
                name = Column(String(50), unique = True, nullable=False)

    """
    __table_args__ = {'extend_existing': True}

    @declared_attr
    def __tablename__(cls):
        def _join(match):
            word = match.group()
            if len(word) > 1:
                return ('_%s_%s' % (word[:-1], word[-1])).lower()
            return '_' + word.lower()

        return _camelcase_re.sub(_join, cls.__name__).lstrip('_')


"""
    This is for retro compatibility
"""
Base = Model

