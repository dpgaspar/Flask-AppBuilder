Model Relations/Composite keys
==============================

On this chapter we are going to show how to setup model relationships and their
view integration on the framework

And the source code for this chapter on
`examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/employees>`_


Many to One
-----------

First let's check the most simple relationship, already described on the quick how to with the contacts
application.

Using a different (and slightly more complex) example. Let's assume we are building a human resources app.
So we have an Employees table with some related data.

- Employee.
- Function.
- Department.

Each Employee belongs to a department and he/she has a particular function.

Let's define our models (models.py)::

    import datetime
    from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
    from sqlalchemy.orm import relationship
    from flask_appbuilder import Model


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


    def today():
        return datetime.datetime.today().strftime('%Y-%m-%d')


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
        begin_date = Column(Date, default=today, nullable=False)
        end_date = Column(Date, nullable=True)

        def __repr__(self):
            return self.full_name


This has two, one to many relations:

  - One employee belongs to a department and a department has many employees

  - One employee executes a function and a function is executed by many employees.

Now let's define ours views (views.py)::

    from flask_appbuilder import ModelView
    from flask_appbuilder.models.sqla.interface import SQLAInterface
    from .models import Employee,Department, Function, EmployeeHistory
    from app import appbuilder


    class EmployeeView(ModelView):
        datamodel = SQLAInterface(Employee)

        list_columns = ['full_name', 'department', 'employee_number']


    class FunctionView(ModelView):
        datamodel = SQLAInterface(Function)
        related_views = [EmployeeView]


    class DepartmentView(ModelView):
        datamodel = SQLAInterface(Department)
        related_views = [EmployeeView]


Has described on the :doc:`quickhowto` chapter the *related_views* property will tell F.A.B
to add the defined **EmployeeView** filtered by the relation on the show and edit form for
the departments and functions. So on the department show view you will have a tab with all
the employees that belong to it, and of course on the function show view you will have a tab
with all the employees that share this function.

Finally register everything to create the flask endpoints and automatic menu construction::

    db.create_all()

    appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
    appbuilder.add_separator("Company")
    appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
    appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")


Remember 'db.create_all()' will create all your models on the database if they do not exist already.

Many to Many
------------

Our employees have benefits, and HR wants to track them. It's time to define a many to many relation.

On your model definition add the benefit model::

    class Benefit(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True, nullable=False)

        def __repr__(self):
            return self.name

Then define the association table between Employee and Benefit,
then add the relation to benefit on the Employee model::

    assoc_benefits_employee = Table('benefits_employee', Model.metadata,
                                          Column('id', Integer, primary_key=True),
                                          Column('benefit_id', Integer, ForeignKey('benefit.id')),
                                          Column('employee_id', Integer, ForeignKey('employee.id'))
    )


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
        benefits = relationship('Benefit', secondary=assoc_benefits_employee, backref='employee')

        begin_date = Column(Date, default=today, nullable=False)
        end_date = Column(Date, nullable=True)

        def __repr__(self):
            return self.full_name

On your views (views.py) it would be nice to create a menu entry for benefits, so that HR can
add the available benefits::

    class BenefitView(ModelView):
        datamodel = SQLAInterface(Benefit)
        related_views = [EmployeeView]
        add_columns = ['name']
        edit_columns = ['name']
        show_columns = ['name']
        list_columns = ['name']

Then register your view::

    appbuilder.add_view(BenefitView, "Benefits", icon="fa-folder-open-o", category="Company")

F.A.B. will add a select2 widget for adding benefit tags to employees, when adding or editing an employee.

Many to Many with extra properties
----------------------------------

Finally we are creating a history of the employee on the company, we want to record all his/her department
changes and when did it occur. This can be done in different ways, this one is useful for our example on
how to use a many to many relation with extra properties. So let's define our employee history model::

    class EmployeeHistory(Model):
        id = Column(Integer, primary_key=True)
        department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
        department = relationship("Department")
        employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
        employee = relationship("Employee")
        begin_date = Column(Date, default=today)
        end_date = Column(Date)

As you can see, this model is related to departments and employees and it has a begin date and end date
when he is/was allocated to it. It's a special kind of association table.

We want the history to be shown on the employee show/detail view, has a list history. for this
we need to create a view for employee history and tell F.A.B to make a relation to it::

    class EmployeeHistoryView(ModelView):
        datamodel = SQLAInterface(EmployeeHistory)
        list_columns = ['department', 'begin_date', 'end_date']

Then change the employee view, this time we do not want a tab to navigate to the relation, we want to show
it on the same page cascading::

    class EmployeeView(ModelView):
        datamodel = SQLAInterface(Employee)
        list_columns = ['full_name', 'department', 'employee_number']
        related_views = [EmployeeHistoryView]
        show_template = 'appbuilder/general/model/show_cascade.html'

We need to register the **EmployeeHistoryView** but without a menu, because it's history will be managed
on the employee detail view::

    appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")


Take a look and run the example on `Employees example <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/employees>`_
It includes extra functionality like readonly fields, pre and post update logic, etc...

Composite Keys
--------------

Composite keys is supported for SQLAlchemy only, you can reference them using SQLAlchemy 'relationship',
and use them on combo boxes and/or related views, take a look at the
`example <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/composite_keys>`_

Notice the use of composite keys to prevent that and Item (server or whatever)
can be on more then a Rack/Datacenter at the same time, and that a Datacenter can't have two racks with the same number

.. note:: This feature is only supported since 1.9.6
