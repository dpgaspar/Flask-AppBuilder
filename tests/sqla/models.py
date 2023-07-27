import enum

from flask_appbuilder import Model
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields, ValidationError
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship


def validate_name(n):
    if n[0] != "A":
        raise ValidationError("Name must start with an A")


class Model1(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())

    def __repr__(self):
        return str(self.field_string)

    def full_concat(self):
        return (
            f"{self.field_string}.{self.field_integer}"
            f".{self.field_float}.{self.field_date}"
        )


def validate_field_string(n):
    if n[0] != "A":
        raise ValidationError("Name must start with an A")


class Model1CustomSchema(BaseModelSchema):
    model_cls = Model1
    field_string = fields.String(validate=validate_name)
    field_integer = fields.Integer(allow_none=True)
    field_float = fields.Float(allow_none=True)
    field_date = fields.Date(allow_none=True)


class Model2(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())
    excluded_string = Column(String(50), default="EXCLUDED")
    default_string = Column(String(50), default="DEFAULT")
    group_id = Column(Integer, ForeignKey("model1.id"), nullable=False)
    group = relationship("Model1")

    def __repr__(self):
        return str(self.field_string)

    def field_method(self):
        return f"{self.field_string}_field_method"


class Model3(Model):
    pk1 = Column(Integer(), primary_key=True)
    pk2 = Column(DateTime(), primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return str(self.field_string)


class Model4(Model):
    id = Column(Integer(), primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    model1_1_id = Column(Integer, ForeignKey("model1.id"), nullable=False)
    model1_1 = relationship("Model1", foreign_keys=[model1_1_id])
    model1_2_id = Column(Integer, ForeignKey("model1.id"), nullable=False)
    model1_2 = relationship("Model1", foreign_keys=[model1_2_id])

    def __repr__(self):
        return str(self.field_string)


class ModelWithProperty(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)

    @property
    def custom_property(self):
        return self.field_string + "_custom"


class TmpEnum(enum.Enum):
    e1 = 1
    e2 = 2
    e3 = 3


class ModelWithEnums(Model):
    id = Column(Integer, primary_key=True)
    enum1 = Column(Enum("e1", "e2", "e3", "e4", name="enum1"))
    enum2 = Column(Enum(TmpEnum))
    enum3 = Column(Enum(TmpEnum), info={"marshmallow_by_value": False})


assoc_parent_child = Table(
    "parent_child",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("parent.id")),
    Column("child_id", Integer, ForeignKey("child.id")),
    UniqueConstraint("parent_id", "child_id"),
)


class ModelMMParent(Model):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    children = relationship("ModelMMChild", secondary=assoc_parent_child)


class ModelMMChild(Model):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())


assoc_parent_child_required = Table(
    "parent_child_required",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("parent_required.id")),
    Column("child_id", Integer, ForeignKey("child_required.id")),
    UniqueConstraint("parent_id", "child_id"),
)


class ModelMMParentRequired(Model):
    __tablename__ = "parent_required"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    children = relationship(
        "ModelMMChildRequired",
        secondary=assoc_parent_child_required,
        info={"required": True},
    )


class ModelMMChildRequired(Model):
    __tablename__ = "child_required"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)


class ModelOMParent(Model):
    __tablename__ = "model_om_parent"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)


class ModelOMChild(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("model_om_parent.id"))
    parent = relationship(
        "ModelOMParent",
        backref=backref("children", cascade="all, delete-orphan"),
        foreign_keys=[parent_id],
    )


class ModelOOParent(Model):
    __tablename__ = "model_oo_parent"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    child = relationship("ModelOOChild", back_populates="parent", uselist=False)


class ModelOOChild(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("model_oo_parent.id"))
    parent = relationship("ModelOOParent", back_populates="child")
