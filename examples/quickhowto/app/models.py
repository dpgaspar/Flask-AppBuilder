import datetime
from flask import Markup
from hashlib import md5
from app import db
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.filemanager import ImageManager
from flask.ext.appbuilder import Base

class Group(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique = True, nullable=False)

    def __repr__(self):
        return self.name

class Gender(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique = True, nullable=False)

    def __repr__(self):
        return self.name

class Contact(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    name =  Column(String(150), unique = True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship("Group")
    gender_id = Column(Integer, ForeignKey('gender.id'))
    gender = relationship("Gender")

    def __repr__(self):
        return self.name
        
