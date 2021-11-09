import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

mindate = datetime.date(datetime.MINYEAR, 1, 1)


class Item(Model):
    id = Column(Integer, primary_key=True)
    serial_number = Column(String, unique=True)
    model = Column(String(150), nullable=False)

    def __repr__(self):
        return "%s (%s)" % (self.model, self.serial_number)


class Datacenter(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))

    def __repr__(self):
        return self.name


class Rack(Model):
    num = Column(Integer, primary_key=True)
    datacenter_id = Column(
        Integer, ForeignKey("datacenter.id"), primary_key=True, nullable=False
    )
    datacenter = relationship("Datacenter")

    def __repr__(self):
        return "%d-%s" % (self.num, self.datacenter)


class Inventory(Model):
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True, nullable=False)
    item = relationship("Item")
    rack_num = Column(Integer, ForeignKey("rack.num"), primary_key=True, nullable=False)
    rack_datacenter_id = Column(
        Integer, ForeignKey("rack.datacenter_id"), nullable=False
    )
    rack = relationship(
        "Rack",
        primaryjoin="and_(Inventory.rack_num==Rack.num, "
        "Inventory.rack_datacenter_id==Rack.datacenter_id)",
    )
