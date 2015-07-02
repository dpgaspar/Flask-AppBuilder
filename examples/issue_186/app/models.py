from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
import sqlalchemy.types as types
from sqlalchemy import UniqueConstraint, Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class LowerCaseString(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        return value.lower()

class Site(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    
    def __repr__(self):
        return self.name
    

class DeviceType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

    def __repr__(self):
        return self.name
        
class Device(Model):
    __table_args__ = (UniqueConstraint('name', 'site_id'),)
    id = Column(Integer, primary_key=True)
    name = Column(LowerCaseString(64), nullable=False)
    description = Column(String(255))
    site_id = Column(Integer, ForeignKey('site.id'))
    site = relationship("Site")
    alias_id = Column(Integer, ForeignKey('device.id'))
    alias = relationship("Device")
    devicetype_id = Column(Integer, ForeignKey("device_type.id"))
    devicetype = relationship("DeviceType")

    def __repr__(self):
        return self.name
        