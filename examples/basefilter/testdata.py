from datetime import datetime
import logging
import random

from app import appbuilder, db
from app.models import Contact, ContactGroup, Gender

log = logging.getLogger(__name__)


def get_random_name(names_list, size=1):
    name_lst = [
        names_list[random.randrange(0, len(names_list))].decode("utf-8").capitalize()
        for i in range(0, size)
    ]
    return " ".join(name_lst)


role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
user1 = appbuilder.sm.add_user(
    "user1", "user1", "test", "user1@fab.org", role_admin, "password"
)
user2 = appbuilder.sm.add_user(
    "user2", "user2", "test", "user2@fab.org", role_admin, "password"
)
user3 = appbuilder.sm.add_user(
    "user3", "user3", "test", "user3@fab.org", role_admin, "password"
)

try:
    db.session.add(ContactGroup(name="Friends"))
    db.session.add(ContactGroup(name="Family"))
    db.session.add(ContactGroup(name="Work"))
    db.session.commit()
except Exception as e:
    log.error("Group creation error: %s", e)
    db.session.rollback()
    exit(1)

try:
    db.session.add(Gender(name="Male"))
    db.session.add(Gender(name="Female"))
    db.session.commit()
except Exception as e:
    log.error("Gender creation error: %s", e)
    db.session.rollback()
    exit(1)

f = open("NAMES.DIC", "rb")
names_list = [x.strip() for x in f.readlines()]

f.close()

j = 1
for i in range(1, 100):
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
    c.changed_on = datetime.now()
    c.created_on = datetime.now()
    if j == 1:
        j += 1
        _user = user1
    elif j == 2:
        j += 1
        _user = user2
    else:
        j = 1
        _user = user3
    c.created_by = _user
    c.changed_by = _user

    db.session.add(c)
    try:
        db.session.commit()
        print("inserted", c)
    except Exception as e:
        log.error("Contact creation error: %s", e)
        db.session.rollback()
