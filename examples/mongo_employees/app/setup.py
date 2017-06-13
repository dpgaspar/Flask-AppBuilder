# -*- coding: utf-8 -*-
from random import randrange

import random
import logging
import datetime
from mongoengine import *
from models import Benefit, Function, Department, Employee, EmployeeHistory

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def get_random_name(names_list, size=1):
    name_lst = [names_list[randrange(0, len(names_list))].capitalize() for i in range(0, size)]
    return " ".join(name_lst)


def get_random_date(y1=1950,y2=2016):
    year = random.choice(range(y1, y2))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    return datetime.date(year, month, day)


def create_employee(names_list, benefits, departments, functions):
    emp = Employee()
    emp.full_name = get_random_name(names_list)
    emp.address = names_list[random.randrange(0, len(names_list))] + ' Street'
    emp.fiscal_number = str(randrange(1111111, 9999999))
    emp.employee_number = str(randrange(1111111, 9999999))
    emp.department = departments[random.randrange(0, len(departments)-1)]
    emp.function = functions[random.randrange(0, len(functions)-1)]
    emp.save()

    emp.update(add_to_set__etags=[get_random_name(names_list), get_random_name(names_list)])

    for i in [0,1]:
        b = benefits[random.randrange(0, len(benefits))]

        Employee.objects(id=emp.id).update_one(push__benefits=b)
        emp.reload()

        Benefit.objects(id=b.id).update_one(push__grantees=emp)
        b.reload()

    h = EmployeeHistory()
    h.employee = emp
    h.department = departments[random.randrange(0, len(departments)-1)]
    h.begin_date = get_random_date(2000, 2014)
    end = datetime.date(h.begin_date.year, 12, 31)
    h.end_date = end
    h.save()

    h = EmployeeHistory()
    h.employee = emp
    h.department = departments[random.randrange(0, len(departments)-1)]
    h.begin_date = end
    h.save()

    print("{0} inserted".format(emp.full_name))


def ez_setup(appbuilder, userclass):

    if not userclass.objects:
        role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
        print('roleadmin=', role_admin)

        u = 'u'
        user = appbuilder.sm.add_user(u, u, u, u, role_admin, u)
        if user:
            print('Admin User "{0}" created.'.format(u))

            if not Benefit.objects:

                benefits = []
                for i in [1,2,3,4,5,6,7,8,9,10]:
                    b = Benefit(name='b' + str(i))
                    b.save(force_insert=True)
                    benefits.append(b)

                departments = []
                for i in [1,2,3,4,5,6,7,8,9,10]:
                    d = Department(name='Dept_' + str(i))
                    d.save(force_insert=True)
                    departments.append(d)

                functions = []
                for i in [1,2,3,4,5,6,7,8,9,10]:
                    f = Function(name = 'Funct_' + str(i))
                    f.save(force_insert=True)
                    functions.append(f)

                f = open('NAMES.DIC', "rb")
                names_list = [x.strip() for x in f.readlines()]

                f.close()
                for i in range(1, 500):
                    create_employee(names_list, benefits, departments, functions)

        else:
            print('No user created, an error occured')



