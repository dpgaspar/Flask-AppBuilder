from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql.schema import Table


class SQLA(SQLAlchemy):
    """
    This is a child class of flask_SQLAlchemy
    It's purpose is to override the declarative base of the original
    package. So that it is bound to F.A.B. Model class allowing the dev
    to be in the same namespace of the security tables (and others)
    and can use AuditMixin class alike.

    Configure just like flask_sqlalchemy SQLAlchemy
    """

    @staticmethod
    def get_tables_for_bind(bind: Engine | Connection) -> list[Table]:
        from sqlalchemy import inspect

        inspector = inspect(bind)
        return inspector.get_table_names()
