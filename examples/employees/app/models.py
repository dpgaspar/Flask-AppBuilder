import datetime
from flask import Markup, url_for
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Date, Text, DateTime
from sqlalchemy.orm import relationship, backref
from flask.ext.appbuilder.filemanager import ImageManager
from flask.ext.appbuilder.models.mixins import BaseMixin, ImageColumn
from flask.ext.appbuilder import Model
from flask_appbuilder.security.models import User


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


class EmployeeHistory(Model):
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship("Department")
    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    employee = relationship("Employee")
    begin_date = Column(Date)
    end_date = Column(Date)



class Employee(Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    address = Column(Text(250), nullable=False)
    fiscal_number = Column(Integer, nullable=False)
    employee_number = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship("Department")
    function_id = Column(Integer, ForeignKey('function.id'), nullable=False)
    function = relationship("Function")
    begin_date = Column(Date, default=datetime.datetime.now, nullable=False)
    end_date = Column(Date, default=datetime.datetime.now, nullable=True)

    def __repr__(self):
        return self.user.first_name

