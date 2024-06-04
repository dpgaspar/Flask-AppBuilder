from datetime import datetime
import logging
import random

from app import db, create_app
from app.models import Contact, ContactGroup, Gender, ModelOMParent, ModelOMChild

log = logging.getLogger(__name__)

app = create_app()


def get_random_name(names_list, size=1):
    name_lst = [
        names_list[random.randrange(0, len(names_list))].decode("utf-8").capitalize()
        for i in range(0, size)
    ]
    return " ".join(name_lst)


def upsert_test_data():
    try:
        db.session.query(Contact).delete()
        db.session.query(ContactGroup).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        groups = []
        groups.append(ContactGroup(name="Friends"))
        groups.append(ContactGroup(name="Family"))
        groups.append(ContactGroup(name="Work"))
        db.session.add(groups[0])
        db.session.add(groups[1])
        db.session.add(groups[2])
        print(groups[0].id)
        db.session.commit()
    except Exception as e:
        log.error("Creating Groups: %s", e)
        db.session.rollback()

    model_oo_parents = list()
    for i in range(20):
        model = ModelOMParent()
        model.field_string = f"text{i}"
        db.session.add(model)
        db.session.commit()
        model_oo_parents.append(model)

    for i in range(20):
        for j in range(1, 4):
            model = ModelOMChild()
            model.field_string = f"text{i}.{j}"
            model.parent = model_oo_parents[i]
            db.session.add(model)
            db.session.commit()

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
        c.gender = random.choice(list(Gender))
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


with app.app_context():
    upsert_test_data()
