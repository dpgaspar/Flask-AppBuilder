import datetime
import logging
import re


from flask_sqlalchemy import SQLAlchemy


from sqlalchemy.orm import DeclarativeBase

try:
    from sqlalchemy.orm.util import identity_key  # noqa

    has_identity_key = True
except ImportError:
    has_identity_key = False

log = logging.getLogger(__name__)

_camelcase_re = re.compile(r"([A-Z]+)(?=[a-z0-9])")


class Model(DeclarativeBase):
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


class SQLA(SQLAlchemy):
    """
    This is a child class of flask_SQLAlchemy
    It's purpose is to override the declarative base of the original
    package. So that it is bound to F.A.B. Model class allowing the dev
    to be in the same namespace of the security tables (and others)
    and can use AuditMixin class alike.

    Use it and configure it just like flask_SQLAlchemy
    """

    def __init__(self, *args, **kwargs):
        model_class = kwargs.pop("model_class", Model)

        super().__init__(*args, model_class=model_class, **kwargs)

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        tables = Model.metadata.tables
        for key in tables:
            if tables[key].info.get("bind_key") == bind:
                result.append(tables[key])
        return result


"""
    This is for retro compatibility
"""
Base = Model
