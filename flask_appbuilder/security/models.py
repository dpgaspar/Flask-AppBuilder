from flask import Markup

from hashlib import md5
from app import db
from config import AUTH_ROLE_ADMIN, AUTH_ROLE_PUBLIC
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.mixins import BaseMixin

def is_menu_public(item):
    """
    Check if menu item has public permissions
    
    param item:
        menu item
    """
    role = Role.query.filter_by(name = AUTH_ROLE_PUBLIC).first()
    lst = role.permissions
    if lst:
        for i in lst:
            if item == i.view_menu.name:
                return  True
        return False
    else: return False

def is_item_public(permission_name, generalview_name):
    """
    Check if view has public permissions
    
    param permission_name:
        the permission: can_show, can_edit...
    param generalview_name:
        the name of the class view (child of BaseView)
    """

    role = Role.query.filter_by(name = AUTH_ROLE_PUBLIC).first()
    lst = role.permissions
    if lst:
        for i in lst:
            if (generalview_name == i.view_menu.name) and (permission_name == i.permission.name):
                return True
        return False
    else: return False



class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique = True, nullable=False)

    def add_unique(self, name):
        perm = Permission.query.filter_by(name = name).first()
        if perm == None:
            perm = Permission()
            perm.name = name
            db.session.add(perm)
            db.session.commit()
            return perm
        return perm

    def __repr__(self):
        return self.name

class ViewMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique = True, nullable=False)


    def add_unique(self, name):
        view_menu = ViewMenu.query.filter_by(name = name).first()
        if view_menu == None:
            view_menu = ViewMenu()
            view_menu.name = name
            db.session.add(view_menu)
            db.session.commit()
            return view_menu
        return view_menu

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self):
        return self.name



class PermissionView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))
    permission = db.relationship("Permission")
    view_menu_id = db.Column(db.Integer, db.ForeignKey('view_menu.id'))
    view_menu = db.relationship("ViewMenu")

    def add_unique(self, permission_name, view_menu_name):
        vm = ViewMenu()
        vm = vm.add_unique(view_menu_name)
        perm = Permission()
        perm = perm.add_unique(permission_name)
        pv = PermissionView()
        pv.view_menu_id, pv.permission_id = vm.id, perm.id
        db.session.add(pv)
        db.session.commit()
        print "Added Permission View " , str(pv)
        return pv


    def _find_permission(self, lst, item):
        for i in lst:
            if i.permission.name == item:
                return True
        return False

    def add_view_permissions(self, base_permissions, view_menu):
        view_menu_db = ViewMenu.query.filter_by(name = view_menu).first()
        if view_menu_db == None:
            view_menu_db = ViewMenu()
            view_menu_db = view_menu_db.add_unique(view_menu)
        lst = PermissionView.query.filter_by(view_menu_id = view_menu_db.id).all()
        # No permissions for this view
        if lst == []:
            for perm_str in base_permissions:
                pv = self.add_unique(perm_str, view_menu)
                role_admin = Role.query.filter_by(name = AUTH_ROLE_ADMIN).first()
                role_admin.add_unique_permission(pv)
        else:
            for item in base_permissions:
                if not self._find_permission(lst, item):
                    pv = self.add_unique(item, view_menu)
                    role_admin = Role.query.filter_by(name = AUTH_ROLE_ADMIN).first()
                    role_admin.add_unique_permission(pv)
            for item in lst:
                if item.permission.name not in base_permissions:
                    # perm to delete
                    pass

    def add_menu_permissions(self, view_menu):
        view_menu_db = ViewMenu.query.filter_by(name = view_menu).first()
        if view_menu_db == None:
            view_menu_db = ViewMenu()
            view_menu_db = view_menu_db.add_unique(view_menu)
        lst = PermissionView.query.filter_by(view_menu_id = view_menu_db.id).all()
        if lst == []:
            pv = self.add_unique('menu_access', view_menu)
            role_admin = Role.query.filter_by(name = AUTH_ROLE_ADMIN).first()
            role_admin.add_unique_permission(pv)

    def __repr__(self):
        return str(self.permission).replace('_',' ') + ' on ' + str(self.view_menu)

assoc_permissionview_role = db.Table('permission_view_role', db.Model.metadata,
        db.Column('permission_view_id', db.Integer, db.ForeignKey('permission_view.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
        )


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique = True, nullable=False)
    permissions = db.relationship('PermissionView', secondary = assoc_permissionview_role, backref='role')


    def add_unique_permission(self, perm_view):
        if perm_view not in self.permissions:
            self.permissions.append(perm_view)
            db.session.merge(self)
            db.session.commit()
            print "Added Role " , str(perm_view) , " to Role " , self.name

    def __repr__(self):
        return self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable = False)
    last_name = db.Column(db.String(64), nullable = False)
    username = db.Column(db.String(32), unique=True, nullable = False)
    password = db.Column(db.String(32))
    active = db.Column(db.Boolean)
    email = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship("Role")

    def has_menu_access(self, menu_name):
        lst = self.role.permissions
        if lst:
            for i in lst:
                if menu_name == i.view_menu.name:
                    return  True
            return False
        else: return False

    def has_permission_on_view(self, permission_name, generalview_name):
        lst = self.role.permissions
        if lst:
            for i in lst:
                if (generalview_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else: return False

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

