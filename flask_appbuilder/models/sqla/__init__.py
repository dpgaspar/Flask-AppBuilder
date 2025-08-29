from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Model(Base):
    __abstract__ = True
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
