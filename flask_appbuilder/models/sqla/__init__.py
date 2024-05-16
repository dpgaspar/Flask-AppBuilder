from __future__ import annotations

import datetime
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.schema import Table


@as_declarative(name="Model", metaclass=DefaultMeta)
class Model:
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

    def to_json(self) -> dict[str, Any]:
        result = {}
        for key in self.__mapper__.c.keys():
            col = getattr(self, key)
            if isinstance(col, (datetime.datetime, datetime.date)):
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

    Configure just like flask_sqlalchemy SQLAlchemy
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        model_class = kwargs.pop("model_class", Model)
        super().__init__(
            *args, model_class=model_class, disable_autonaming=True, **kwargs
        )

    @staticmethod
    def get_tables_for_bind(bind: Engine | Connection) -> list[Table]:
        """Returns a list of all tables relevant for a bind."""
        tables = Model.metadata.tables
        return [
            table for key, table in tables.items() if table.info.get("bind_key") == bind
        ]
