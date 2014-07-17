import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder import Model


class Parent(Model):
 
    """ Contains the fields of the deliverable list. """
 
    __tablename__ = 'parent'
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Float, nullable=False)
    name = Column(String)
 
class Child(Model):
 
    """ Contains the fields of the deliverable list. """
 
    __tablename__ = 'child'
 
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    number = Column(Float, nullable=False)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
 
    parent = relationship('Parent')

