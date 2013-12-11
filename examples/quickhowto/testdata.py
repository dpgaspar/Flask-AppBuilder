from app import db
from app.models import Group, Contact
import random
from datetime import datetime
import sys

def get_random_name(names_list, size = 1):    
    name_lst =  [names_list[random.randrange(0,len(names_list))].capitalize() for i in range(0, size)]
    return " ".join(name_lst)
         

g1 = Group()
g1.name = 'Friends'
g2 = Group()
g2.name = 'Family'
g3 = Group()
g3.name = 'Work'
try:
    db.session.add(g1)
    db.session.add(g2)
    db.session.add(g3)
    db.session.commit()
except:
    db.session.rollback()

f = open('NAMES.DIC', "rb")
names_list = [x.strip() for x in f.readlines()]
    
f.close()



for i in range(1,100):
    c = Contact()
    c.name = get_random_name(names_list, random.randrange(2,6)) 
    c.address = 'Street ' + names_list[random.randrange(0,len(names_list))]
    c.personal_phone = random.randrange(1111111,9999999)
    c.personal_celphone = random.randrange(1111111,9999999)
    c.group_id = random.randrange(1,4)
    year = random.choice(range(1900, 2012))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    c.birthday  = datetime(year, month, day)
    db.session.add(c)
    try:
        db.session.commit()
        print "inserted", c
    except:
        db.session.rollback()
    
    
