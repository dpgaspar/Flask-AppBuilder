import datetime
import math

from flask import Markup
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

mindate = datetime.date(datetime.MINYEAR, 1, 1)


class ContactGroup(Model):
    __tablename__ = "contact_group"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def extra_col(self):
        return "EXTRA {0}".format(self.id)

    @renders("name")
    def extra_col2(self):
        return Markup("<h2>" + self.name + "</h2>")

    def __repr__(self):
        return self.name


class ProductManufacturer(Model):
    __tablename__ = "product_manufacturer"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ProductModel(Model):
    __tablename__ = "product_model"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    product_manufacturer_id = Column(
        Integer, ForeignKey("product_manufacturer.id"), nullable=False
    )
    product_manufacturer = relationship("ProductManufacturer")

    def __repr__(self):
        return self.name


class Product(Model):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    product_manufacturer_id = Column(
        Integer, ForeignKey("product_manufacturer.id"), nullable=False
    )
    product_manufacturer = relationship("ProductManufacturer")
    product_model_id = Column(Integer, ForeignKey("product_model.id"), nullable=False)
    product_model = relationship("ProductModel")

    def __repr__(self):
        return self.name


class Gender(Model):
    __tablename__ = "gender"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


def test():
    return math.pi - 1.0


class FloatModel(Model):
    __tablename__ = "float_model"
    id = Column(Integer, primary_key=True)
    value = Column(Float, nullable=False, default=test)
    value_numeric = Column(Numeric, nullable=False, default=test)

    def __repr__(self):
        return self.value


class Contact(Model):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey("contact_group.id"), nullable=False)
    contact_group = relationship("ContactGroup")
    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False)
    gender = relationship("Gender")

    def __repr__(self):
        return "%s : %s\n" % (self.name, self.contact_group)

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)
