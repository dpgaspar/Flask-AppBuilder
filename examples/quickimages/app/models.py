import datetime
from flask import Markup
from hashlib import md5
from app import db
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.filemanager import ImageManager


class Group(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(50), unique = True, nullable=False)
    address =  db.Column(db.String(264))
    phone1 = db.Column(db.String(20))
    phone2 = db.Column(db.String(20))
    taxid = db.Column(db.Integer)
    notes = db.Column(db.Text())

    def __repr__(self):
        return self.name


class Person(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(150), unique = True, nullable=False)
    address =  db.Column(db.String(564))
    birthday = db.Column(db.Date)
    photo = db.Column(ImageColumn, nullable=False )
    personal_phone = db.Column(db.String(20))
    personal_celphone = db.Column(db.String(20))
    personal_email = db.Column(db.String(64))
    notes = db.Column(db.Text())
    business_function = db.Column(db.String(64))
    business_phone = db.Column(db.String(20))
    business_celphone = db.Column(db.String(20))
    business_email = db.Column(db.String(64))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship("Group")


    def photo_img(self):
        im = ImageManager()
        if self.photo:
            return Markup('<a href="/persons/show/' + str(self.id) + '" class="thumbnail"><img src="' + im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="/persons/show/' + str(self.id) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        
