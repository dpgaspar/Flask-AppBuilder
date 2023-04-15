import datetime
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

from ..const import MODELOMCHILD_DATA_SIZE


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
    e1 = "a"
    e2 = 2
    e3 = 3


class ModelWithEnums(Model):
    id = Column(Integer, primary_key=True)
    enum1 = Column(Enum("e1", "e2", "e3", name="enum1"))
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

    """ ---------------------------------
            TEST HELPER FUNCTIONS
        ---------------------------------
    """


def insert_model1(session, i=0):
    add_flag = False
    model = session.query(Model1).filter_by(id=i + 1).one_or_none()
    if not model:
        model = Model1()
        add_flag = True
    model.field_string = f"test{i}"
    model.field_integer = i
    model.field_float = float(i)
    if add_flag:
        session.add(model)
    session.commit()
    return model


def insert_model2(session, i=0, model1_collection=None):
    if not model1_collection:
        model1 = session.query(Model1).filter_by(id=i + 1).one_or_none()
    else:
        model1 = model1_collection[i]
    model = Model2()
    model.field_string = f"test{i}"
    model.field_integer = i
    model.field_float = float(i)
    model.group = model1

    import random

    year = random.choice(range(1900, 2012))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    model.field_date = datetime.datetime(year, month, day)

    session.add(model)
    session.commit()
    return model


def insert_model3(session):
    model3 = Model3(pk1=3, pk2=datetime.datetime(2017, 3, 3), field_string="foo")
    try:
        session.add(model3)
        session.commit()
    except Exception as e:
        print("Error {0}".format(str(e)))
        session.rollback()


def insert_model_mm_parent(session, i=0, children=None):
    add_flag = False
    model = session.query(ModelMMParent).filter_by(id=i + 1).one_or_none()
    if not model:
        model = ModelMMParent()
        add_flag = True
    model.field_string = str(i)
    if children:
        model.children = children
    if add_flag:
        session.add(model)
    session.commit()
    return model


def insert_model_with_enums(session, i=0):
    add_flag = False
    model = session.query(ModelWithEnums).filter_by(id=i + 1).one_or_none()
    if not model:
        model = ModelWithEnums()
        add_flag = True
    model.enum1 = "e1"
    model.enum2 = TmpEnum.e2
    if add_flag:
        session.add(model)
    session.commit()
    return model


def insert_data(session, count):
    model1_collection = list()
    # Fill model1
    for i in range(count):
        model = insert_model1(session, i)
        model1_collection.append(model)
    # Fill model2
    for i in range(count):
        insert_model2(session, i=i, model1_collection=model1_collection)
    insert_model3(session)

    for i in range(count):
        model = ModelWithEnums()
        model.enum1 = "e1"
        model.enum2 = TmpEnum.e2
        session.add(model)
        session.commit()
    # Fill Model4
    for i in range(count):
        model = Model4()
        model.field_string = f"test{i}"
        model.model1_1 = model1_collection[i]
        model.model1_2 = model1_collection[i]
        session.add(model)
        session.commit()

    children = list()
    children_required = list()
    for i in range(1, 4):
        model = ModelMMChild()
        model.field_string = str(i)
        model.field_integer = i
        children.append(model)
        session.add(model)
        session.commit()

        model = ModelMMChildRequired()
        model.field_string = str(i)
        children_required.append(model)
        session.add(model)
        session.commit()

    for i in range(count):
        insert_model_mm_parent(session, i=i, children=children)

        model = ModelMMParentRequired()
        model.field_string = str(i)
        model.children = children_required
        session.add(model)
        session.commit()

    for i in range(count):
        model = ModelWithProperty()
        model.field_string = str(i)
        session.add(model)
        session.commit()

    model_om_parents = list()
    for i in range(count):
        model = ModelOMParent()
        model.field_string = f"text{i}"
        session.add(model)
        session.commit()
        model_om_parents.append(model)

    for i in range(count):
        for j in range(1, MODELOMCHILD_DATA_SIZE):
            model = ModelOMChild()
            model.field_string = f"text{i}.{j}"
            model.parent = model_om_parents[i]
            session.add(model)
            session.commit()

    for i in range(count):
        model = ModelOOParent()
        model.field_string = f"text{i}"
        model.child = ModelOOChild(field_string=f"text{i}.child")
        session.add(model)
        session.commit()
