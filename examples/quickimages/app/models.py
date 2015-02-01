import datetime
from flask import Markup, url_for
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app import db
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.filemanager import ImageManager
from flask.ext.appbuilder import Model


class PersonGroup(Model):
    id = Column(Integer, primary_key=True)
    name =  Column(String(50), unique = True, nullable=False)
    address = Column(String(264))
    phone1 = Column(String(20))
    phone2 = Column(String(20))
    taxid = Column(Integer)
    notes = Column(Text())

    def __repr__(self):
        return self.name


class Person(Model):
    id = Column(Integer, primary_key=True)
    name =  Column(String(150), unique = True, nullable=False)
    address =  Column(String(564))
    birthday = Column(Date)
    photo = Column(ImageColumn(thumbnail_size=(30, 30, True), size=(300, 300, True)))
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    personal_email = Column(String(64))
    notes = Column(Text())
    business_function = Column(String(64))
    business_phone = Column(String(20))
    business_celphone = Column(String(20))
    business_email = Column(String(64))
    person_group_id = Column(Integer, ForeignKey('person_group.id'))
    person_group = relationship("PersonGroup")

    def photo_img(self):
        im = ImageManager()
        if self.photo:
            return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                          '" class="thumbnail"><img src="' + im.get_url(self.photo) +\
                          '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="'+ url_for('PersonModelView.show',pk=str(self.id)) +\
                          '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')

    def photo_img_thumbnail(self):
        im = ImageManager()
        if self.photo:
            return Markup('<a href="' + url_for('PersonModelView.show',pk=str(self.id)) +\
                          '" class="thumbnail"><img src="' + im.get_url_thumbnail(self.photo) +\
                          '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="'+ url_for('PersonModelView.show',pk=str(self.id)) +\
                          '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        
