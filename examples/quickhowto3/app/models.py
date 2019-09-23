from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask_appbuilder.models.mixins import (
    AuditMixin,
    BaseMixin,
    FileColumn,
    ImageColumn,
)
from flask_appbuilder import Model


class Group(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Gender(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Contact(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False)
    group = relationship("Group")
    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False)
    gender = relationship("Gender")

    def __repr__(self):
        return self.name
