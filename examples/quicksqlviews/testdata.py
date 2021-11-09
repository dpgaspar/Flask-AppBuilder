import logging
from app import db
from app.models import ContactGroup, Gender, Contact
import random
from datetime import datetime

log = logging.getLogger(__name__)


def get_random_name(names_list, size=1):
    name_lst = [
        names_list[random.randrange(0, len(names_list))].decode("utf-8").capitalize()
        for i in range(0, size)
    ]
    return " ".join(name_lst)


try:
    db.session.query(Contact).delete()
    db.session.query(Gender).delete()
    db.session.query(ContactGroup).delete()
    db.session.commit()
except:
    db.session.rollback()

try:
    groups = []
    groups.append(ContactGroup(name="Friends"))
    groups.append(ContactGroup(name="Family"))
    groups.append(ContactGroup(name="Work"))
    db.session.add(groups[0])
    db.session.add(groups[1])
    db.session.add(groups[2])
    db.session.commit()
except Exception as e:
    log.error("Creating Groups: %s", e)
    db.session.rollback()

try:
    genders = list()
    genders.append(Gender(name="Male"))
    genders.append(Gender(name="Female"))
    db.session.add(genders[0])
    db.session.add(genders[1])
    db.session.commit()
except Exception as e:
    log.error("Creating Genders: %s", e)
    db.session.rollback()

f = open("NAMES.DIC", "rb")
names_list = [x.strip() for x in f.readlines()]

f.close()

for i in range(1, 1000):
    c = Contact()
    c.name = get_random_name(names_list, random.randrange(2, 6))
    c.address = "Street " + names_list[random.randrange(0, len(names_list))].decode(
        "utf-8"
    )
    c.personal_phone = random.randrange(1111111, 9999999)
    c.personal_celphone = random.randrange(1111111, 9999999)
    c.contact_group = groups[random.randrange(0, 3)]
    c.gender = genders[random.randrange(0, 2)]
    year = random.choice(range(1900, 2012))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    c.birthday = datetime(year, month, day)
    db.session.add(c)
    try:
        db.session.commit()
        print("inserted", c)
    except Exception as e:
        log.error("Creating Contact: %s", e)
        db.session.rollback()
