import string
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from flask_appbuilder import Model, SQLA

import enum


class Model1(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())

    def __repr__(self):
        return str(self.field_string)


class Model2(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())
    excluded_string = Column(String(50), default='EXCLUDED')
    default_string = Column(String(50), default='DEFAULT')
    group_id = Column(Integer, ForeignKey('model1.id'), nullable=False)
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
    e1 = 'a'
    e2 = 2

class ModelWithEnums(Model):
    id = Column(Integer, primary_key=True)
    enum1 = Column(Enum('e1', 'e2'))
    enum2 = Column(Enum(TmpEnum))



    """ ---------------------------------
            TEST HELPER FUNCTIONS
        ---------------------------------
    """

def insert_data(session, Model1, count):
    for i in range(count):
        model = Model1(field_string="test{}".format(i),
                       field_integer=i,
                       field_float=float(i))
        session.add(model)
        session.commit()
