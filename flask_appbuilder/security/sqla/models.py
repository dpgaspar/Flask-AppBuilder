import datetime
from typing import List, Optional

from flask import g
from flask_appbuilder import Model
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.extensions import db
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, Mapped, mapped_column, relationship


_dont_audit = False


class Permission(Model):
    __tablename__ = "ab_permission"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("ab_permission_id_seq", start=1, increment=1, minvalue=1, cycle=False),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ViewMenu(Model):
    __tablename__ = "ab_view_menu"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("ab_view_menu_id_seq", start=1, increment=1, minvalue=1, cycle=False),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self):
        return self.name


assoc_permissionview_role = db.Table(
    "ab_permission_view_role",
    Column(
        "id",
        Integer,
        Sequence(
            "ab_permission_view_role_id_seq",
            start=1,
            increment=1,
            minvalue=1,
            cycle=False,
        ),
        primary_key=True,
    ),
    Column("permission_view_id", Integer, ForeignKey("ab_permission_view.id")),
    Column("role_id", Integer, ForeignKey("ab_role.id")),
    UniqueConstraint("permission_view_id", "role_id"),
)


assoc_user_role = db.Table(
    "ab_user_role",
    Column(
        "id",
        Integer,
        Sequence("ab_user_role_id_seq", start=1, increment=1, minvalue=1, cycle=False),
        primary_key=True,
    ),
    Column("user_id", Integer, ForeignKey("ab_user.id")),
    Column("role_id", Integer, ForeignKey("ab_role.id")),
    UniqueConstraint("user_id", "role_id"),
)


class Role(Model):
    __tablename__ = "ab_role"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("ab_role_id_seq", start=1, increment=1, minvalue=1, cycle=False),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    permissions: Mapped[List["PermissionView"]] = relationship(
        "PermissionView",
        secondary=assoc_permissionview_role,
        backref="role",
    )
    user: Mapped[List["User"]] = relationship(
        "User", secondary=assoc_user_role, backref="roles", enable_typechecks=False
    )

    def __repr__(self):
        return self.name


class PermissionView(Model):
    __tablename__ = "ab_permission_view"
    __table_args__ = (UniqueConstraint("permission_id", "view_menu_id"),)
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(
            "ab_permission_view_id_seq", start=1, increment=1, minvalue=1, cycle=False
        ),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("ab_permission.id"))
    permission: Mapped[Permission] = relationship("Permission", lazy="joined")
    view_menu_id: Mapped[int] = mapped_column(Integer, ForeignKey("ab_view_menu.id"))
    view_menu: Mapped[ViewMenu] = relationship("ViewMenu", lazy="joined")

    def __repr__(self):
        return str(self.permission).replace("_", " ") + " on " + str(self.view_menu)


class User(Model):
    __tablename__ = "ab_user"
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("ab_user_id_seq", start=1, increment=1, minvalue=1, cycle=False),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(256))
    active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True
    )
    login_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fail_login_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_on: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(), nullable=True
    )
    changed_on: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(), nullable=True
    )

    @declared_attr
    def created_by_fk(self) -> Column:
        return Column(
            Integer, ForeignKey("ab_user.id"), default=self.get_user_id, nullable=True
        )

    @declared_attr
    def changed_by_fk(self) -> Column:
        return Column(
            Integer, ForeignKey("ab_user.id"), default=self.get_user_id, nullable=True
        )

    created_by: Mapped["User"] = relationship(
        "User",
        backref=backref("created", uselist=True),
        remote_side=[id],
        primaryjoin="User.created_by_fk == User.id",
        uselist=False,
    )
    changed_by: Mapped["User"] = relationship(
        "User",
        backref=backref("changed", uselist=True),
        remote_side=[id],
        primaryjoin="User.changed_by_fk == User.id",
        uselist=False,
    )

    @classmethod
    def get_user_id(cls):
        try:
            return g.user.id
        except Exception:
            return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return as_unicode(self.id)

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return self.get_full_name()


class RegisterUser(Model):
    __tablename__ = "ab_register_user"
    id = mapped_column(
        Integer,
        Sequence(
            "ab_register_user_id_seq", start=1, increment=1, minvalue=1, cycle=False
        ),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    registration_date: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(), nullable=True
    )
    registration_hash: Mapped[Optional[str]] = mapped_column(String(256))
