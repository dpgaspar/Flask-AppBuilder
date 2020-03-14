import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table, Text, Float, Numeric   # <<--included Numeric
from sqlalchemy.types import DECIMAL                                                            # <<--included DECIMAL
from sqlalchemy.orm import relationship 


class Department(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Function(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Benefit(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


assoc_benefits_employee = Table(
    "benefits_employee",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("benefit_id", Integer, ForeignKey("benefit.id")),
    Column("employee_id", Integer, ForeignKey("employee.id")),
)


def today():
    return datetime.datetime.today().strftime("%Y-%m-%d")


class EmployeeHistory(Model):
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department")
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    employee = relationship("Employee")
    begin_date = Column(Date, default=today)
    end_date = Column(Date)


class Employee(Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    address = Column(Text(250), nullable=False)
    fiscal_number = Column(Integer, nullable=False)
    employee_number = Column(Integer, nullable=False)

	# INCLUDED column/fiedl 'salary' wich is a numeric type with decimals places
    salary = Column(Numeric(precision=14, scale=4, decimal_return_scale=5, asdecimal=True), nullable=False) # CAN use this type with Sqlite
    #salary = Column(DECIMAL(precision=14, scale=4, decimal_return_scale=5, asdecimal=True), nullable=False) # or this type
    #salary = Column(Float(precision=14, decimal_return_scale=5, asdecimal=False), nullable=False)           # or this type

    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department")
    function_id = Column(Integer, ForeignKey("function.id"), nullable=False)
    function = relationship("Function")
    benefits = relationship(
        "Benefit", secondary=assoc_benefits_employee, backref="employee"
    )

    begin_date = Column(Date, default=datetime.date.today(), nullable=True) #It's nullable, but 'default' is used for Nulls
    end_date = Column(Date, nullable=True)           # <<- NO default value for this field - Ok: Null inputs/outputs are being handled


    def __repr__(self):
        return self.full_name

