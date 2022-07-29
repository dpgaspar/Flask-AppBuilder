from datetime import datetime
import random

from flask import current_app
from app.app import create_app
from app.models import Contact, ContactGroup, Gender

app = create_app("config")
app.app_context().push()


def get_random_name(names_list, size=1):
    name_lst = [
        names_list[random.randrange(0, len(names_list))].decode("utf-8").capitalize()
        for i in range(0, size)
    ]
    return " ".join(name_lst)


try:
    current_app.appbuilder.session.add(ContactGroup(name="Friends"))
    current_app.appbuilder.session.add(ContactGroup(name="Family"))
    current_app.appbuilder.session.add(ContactGroup(name="Work"))
    current_app.appbuilder.session.commit()
except Exception:
    current_app.appbuilder.session.rollback()

try:
    current_app.appbuilder.session.add(Gender(name="Male"))
    current_app.appbuilder.session.add(Gender(name="Female"))
    current_app.appbuilder.session.commit()
except Exception:
    current_app.appbuilder.session.rollback()

f = open("NAMES.DIC", "rb")
names_list = [x.strip() for x in f.readlines()]

f.close()

for i in range(1, 50):
    c = Contact()
    c.name = get_random_name(names_list, random.randrange(2, 6))
    c.address = "Street " + names_list[random.randrange(0, len(names_list))].decode(
        "utf-8"
    )
    c.personal_phone = random.randrange(1111111, 9999999)
    c.personal_celphone = random.randrange(1111111, 9999999)
    c.contact_group_id = random.randrange(1, 4)
    c.gender_id = random.randrange(1, 3)
    year = random.choice(range(1900, 2012))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    c.birthday = datetime(year, month, day)
    current_app.appbuilder.session.add(c)
    try:
        current_app.appbuilder.session.commit()
        print("inserted {0}".format(c))
    except Exception:
        current_app.appbuilder.session.rollback()
