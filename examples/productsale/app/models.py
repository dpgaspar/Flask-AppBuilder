import datetime
from flask import Markup, url_for
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app import db
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.filemanager import ImageManager
from flask.ext.appbuilder import Base

class ProductType(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    name =  Column(String(50), unique = True, nullable=False)

    def __repr__(self):
       self.name

class Product(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    name =  Column(String(50), unique = True, nullable=False)
    price =  Column(Float)
    photo = Column(ImageColumn)
    description = Column(Text())
    product_type_id = Column(Integer, ForeignKey('product_type.id'), nullable=False)
    product_type = relationship("ProductType")

    def photo_img(self):
        im = ImageManager()
        if self.photo:
            return Markup('<a href="' + url_for('ProductGeneralView.show',pk=str(self.id)) + '" class="thumbnail"><img src="' + im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="'+ url_for('ProductGeneralView.show',pk=str(self.id)) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')


    def __repr__(self):
        return self.name


class Sale(BaseMixin, Base):
    id = Column(Integer, primary_key=True)
    sold_to_id = Column(Integer, ForeignKey('ab_user.id'))
    sold_to = relationship("User")
    sold_on = Column(Date)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product")
    quantity = Column(Integer)

