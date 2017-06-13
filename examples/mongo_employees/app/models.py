# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import datetime
from mongoengine import Document, DateTimeField, StringField, ReferenceField, ListField, IntField


class Department(Document):
    meta = {'ordering': ['name', ], }

    name = StringField(unique=True, required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class Function(Document):
    meta = {'ordering': ['name', ], }

    name = StringField(unique=True, required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class Benefit(Document):
    meta = {'ordering': ['name', ], }

    name = StringField(unique=True, required=True)
    grantees = ListField(ReferenceField('Employee'))  # many to many -> employee

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


def today():
    return datetime.datetime.today().strftime('%Y-%m-%d')


class EmployeeHistory(Document):
    meta = {'ordering': ['employee', ], }

    employee = ReferenceField("Employee", required=True)
    department = ReferenceField("Department", required=True)
    begin_date = DateTimeField(default=today)
    end_date = DateTimeField()


class Employee(Document):
    meta = {'ordering': ['full_name', ], }

    full_name = StringField(required=True)
    address = StringField(required=True)
    fiscal_number = IntField(required=True)
    employee_number = IntField(required=True)

    department = ReferenceField("Department", required=True)
    function = ReferenceField("Function", required=True)
    benefits = ListField(ReferenceField('Benefit'))  # many to many -> Benefit

    etags = ListField(StringField())  # for search tests

    begin_date = DateTimeField(default=datetime.date.today())
    end_date = DateTimeField(default=datetime.date.today())

    def __unicode__(self):
        return self.full_name

    def __repr__(self):
        return self.full_name
