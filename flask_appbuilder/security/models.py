from flask import Markup

from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.mixins import BaseMixin


try:
    from app import db
except ImportError:
    raise Exception('db not found please use required skeleton application see documentation')



class Permission(db.Model):
    __tablename__ = 'ab_permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique = True, nullable=False)

    def __repr__(self):
        return self.name

class ViewMenu(db.Model):
    __tablename__ = 'ab_view_menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique = True, nullable=False)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self):
        return self.name

class PermissionView(db.Model):
    __tablename__ = 'ab_permission_view'
    id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('ab_permission.id'))
    permission = db.relationship("Permission")
    view_menu_id = db.Column(db.Integer, db.ForeignKey('ab_view_menu.id'))
    view_menu = db.relationship("ViewMenu")

    def __repr__(self):
        return str(self.permission).replace('_',' ') + ' on ' + str(self.view_menu)

assoc_permissionview_role = db.Table('ab_permission_view_role', db.Model.metadata,
        db.Column('permission_view_id', db.Integer, db.ForeignKey('ab_permission_view.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('ab_role.id'))
        )


class Role(db.Model):
    __tablename__ = 'ab_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique = True, nullable=False)
    permissions = db.relationship('PermissionView', secondary = assoc_permissionview_role, backref='ab_role')

    def __repr__(self):
        return self.name


class User(db.Model):
    __tablename__ = 'ab_user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable = False)
    last_name = db.Column(db.String(64), nullable = False)
    username = db.Column(db.String(32), unique=True, nullable = False)
    password = db.Column(db.String(32))
    active = db.Column(db.Boolean)
    email = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('ab_role.id'))
    role = db.relationship("Role")

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def __repr__(self):
        return (self.get_full_name())

