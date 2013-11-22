import datetime
from flask import Markup
from hashlib import md5
from app import db
from flask.ext.appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from flask.ext.appbuilder.filemanager import ImageManager


class Group(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(50), unique = True, nullable=False)

    def __repr__(self):
        return self.name


class Contact(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(150), unique = True, nullable=False)
    address =  db.Column(db.String(564))
    birthday = db.Column(db.Date, nullable=True)
    personal_phone = db.Column(db.String(20))
    personal_celphone = db.Column(db.String(20))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship("Group")

