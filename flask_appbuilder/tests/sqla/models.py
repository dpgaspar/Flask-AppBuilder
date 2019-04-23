import enum

from flask_appbuilder import Model
from marshmallow import ValidationError
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
    UniqueConstraint
)
from sqlalchemy.orm import relationship


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
        return "{}.{}.{}.{}".format(
            self.field_string, self.field_integer, self.field_float, self.field_date
        )


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
        return "field_method_value"


class Model3(Model):
    pk1 = Column(Integer(), primary_key=True)
    pk2 = Column(DateTime(), primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return str(self.field_string)


class TmpEnum(enum.Enum):
    e1 = "a"
    e2 = 2


class ModelWithEnums(Model):
    id = Column(Integer, primary_key=True)
    enum1 = Column(Enum("e1", "e2"))
    enum2 = Column(Enum(TmpEnum), info={"enum_class": TmpEnum})


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
        info={"required": True}
    )


class ModelMMChildRequired(Model):
    __tablename__ = "child_required"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)

    """ ---------------------------------
            TEST HELPER FUNCTIONS
        ---------------------------------
    """


def insert_data(session, count):
    model1_collection = list()
    for i in range(count):
        model = Model1()
        model.field_string = "test{}".format(i)
        model.field_integer = i
        model.field_float = float(i)
        session.add(model)
        session.commit()
        model1_collection.append(model)
    for i in range(count):
        model = Model2()
        model.field_string = "test{}".format(i)
        model.field_integer = i
        model.field_float = float(i)
        model.group = model1_collection[i]
        session.add(model)
        session.commit()
    for i in range(count):
        model = ModelWithEnums()
        model.enum1 = "e1"
        model.enum2 = TmpEnum.e2
        session.add(model)
        session.commit()

    children = list()
    children_required = list()
    for i in range(1, 4):
        model = ModelMMChild()
        model.field_string = str(i)
        children.append(model)
        session.add(model)
        session.commit()

        model = ModelMMChildRequired()
        model.field_string = str(i)
        children_required.append(model)
        session.add(model)
        session.commit()

    for i in range(count):
        model = ModelMMParent()
        model.field_string = str(i)
        model.children = children
        session.add(model)
        session.commit()

        model = ModelMMParentRequired()
        model.field_string = str(i)
        model.children = children_required
        session.add(model)
        session.commit()
