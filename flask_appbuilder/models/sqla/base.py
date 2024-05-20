from __future__ import annotations

from flask import Flask
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

    def init_app(self, app: Flask) -> None:
        session_options = app.config.get("SQLALCHEMY_SESSION_OPTIONS", {})
        if session_options:
            self.session = self._make_scoped_session(session_options)
        super().init_app(app)

    def get_tables_for_bind(self, bind: Engine | Connection) -> list[Table]:
        """Returns a list of all tables relevant for a bind."""
        tables = self.metadata.tables
        return [
            table for key, table in tables.items() if table.info.get("bind_key") == bind
        ]
