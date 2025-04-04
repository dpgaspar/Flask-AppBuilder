import datetime
import enum
from typing import Optional, List

from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Enum, Table
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column


mindate = datetime.date(datetime.MINYEAR, 1, 1)


class ContactGroup(AuditMixin, Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ContactGroupTag(Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("contact_group.id"), nullable=True
    )
    groups: Mapped[List[ContactGroup]] = relationship(
        ContactGroup,
        backref=backref("tags"),
        secondary="group_tag_association"
    )

# Association Table for N-N Relationship
group_tag_association = Table(
    'group_tag_association',
    Model.metadata,
    Column('group_id', Integer, ForeignKey('contact_group.id')),
    Column('tag_id', Integer, ForeignKey('contact_group_tag.id'))
)

class Gender(enum.Enum):
    Female = 1
    Male = 2


class Contact(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey("contact_group.id"), nullable=False)
    contact_group = relationship("ContactGroup")
    gender = Column(Enum(Gender), info={"marshmallow_by_value": False})

    def __repr__(self):
        return self.name

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)


class ModelOMParent(Model):
    __tablename__ = "model_om_parent"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)


class ModelOMChild(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("model_om_parent.id"))
    parent = relationship(
        "ModelOMParent",
        backref=backref("children", cascade="all, delete-orphan"),
        foreign_keys=[parent_id],
    )
