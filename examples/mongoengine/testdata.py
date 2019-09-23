from app.models import ContactGroup, Gender, Contact
import random
from datetime import datetime


def get_random_name(names_list, size=1):
    name_lst = [
        names_list[random.randrange(0, len(names_list))].decode("utf-8").capitalize()
        for i in range(0, size)
    ]
    return " ".join(name_lst)


ContactGroup.drop_collection()
Gender.drop_collection()
Contact.drop_collection()

g1 = ContactGroup(name="Friends").save()
g2 = ContactGroup(name="Family").save()
g3 = ContactGroup(name="Work").save()
groups = [g1, g2, g3]

gender1 = Gender(name="Male").save()
gender2 = Gender(name="Female").save()
genders = [gender1, gender2]

f = open("NAMES.DIC", "rb")
names_list = [x.strip() for x in f.readlines()]

f.close()

for i in range(1, 1000):
    c = Contact()
    c.name = get_random_name(names_list, random.randrange(2, 6))
    c.address = "Street " + names_list[random.randrange(0, len(names_list))].decode(
        "utf-8"
    )
    c.personal_phone = str(random.randrange(1111111, 9999999))
    c.personal_celphone = str(random.randrange(1111111, 9999999))
    c.contact_group = groups[random.randrange(0, 3)]
    c.gender = genders[random.randrange(0, 2)]
    year = random.choice(range(1900, 2012))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))
    c.birthday = datetime(year, month, day)
    c.save()
    print("{0} inserted".format(c.name))
