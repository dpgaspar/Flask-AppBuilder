import logging
import re
from functools import partial
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine


log = logging.getLogger(__name__)

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def create_scoped_session(app):
    """Helper factory method that creates a scoped session.  It
    internally calls :meth:`create_session`.
    """
    return scoped_session(partial(create_session, app))


def create_session(app):
    return SingleSession(app)


class SingleSession(Session):
    def __init__(self, app, autocommit=False, autoflush=True, **options):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Session.__init__(self, autocommit=autocommit, autoflush=autoflush,
                         bind=engine, **options)


@as_declarative(name='Model')
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

