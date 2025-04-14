from __future__ import annotations

import datetime
from typing import Optional

from flask_appbuilder import Model
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

try:
    from sqlalchemy.orm import mapped_column
except ImportError:
    # fallback for SQLAlchemy < 2.0
    def mapped_column(*args, **kwargs):
        from sqlalchemy import Column
        return Column(*args, **kwargs)


mindate = datetime.date(datetime.MINYEAR, 1, 1)


class ContactGroup(Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Gender(Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Contact(Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(564))
    birthday: Mapped[Optional[datetime.date]] = mapped_column(Date)
    personal_phone: Mapped[Optional[str]] = mapped_column(String(20))
    personal_celphone: Mapped[Optional[str]] = mapped_column(String(20))
    contact_group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contact_group.id"), nullable=False
    )
    contact_group: Mapped[ContactGroup] = relationship("ContactGroup")
    gender_id: Mapped[int] = mapped_column(Integer, ForeignKey("gender.id"), nullable=False)
    gender: Mapped[Gender] = relationship("Gender")

    def __repr__(self):
        return self.name

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)
