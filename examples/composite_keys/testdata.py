import logging
from app import create_app
from app.models import Datacenter, Rack, Item
from flask_appbuilder.extensions import db
import random
import string

log = logging.getLogger(__name__)

DC_RACK_MAX = 20
ITEM_MAX = 1000

cities = ["Lisbon", "Porto", "Madrid", "Barcelona", "Frankfurt", "London"]

models = ["Server MX", "Server MY", "Server DL380", "Server x440", "Server x460"]

datacenters = list()

app = create_app()


def get_random_name(names_list, size=1):
    return names_list[random.randrange(0, len(names_list))]


def serial_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def upsert_test_data():
    for city in cities:
        datacenter = Datacenter()
        datacenter.name = "DC %s" % city
        datacenter.address = city
        datacenters.append(datacenter)
        db.session.add(datacenter)
        log.info(datacenter)
        try:
            db.session.commit()
            for num in range(1, DC_RACK_MAX):
                rack = Rack()
                rack.num = num
                rack.datacenter = datacenter
                db.session.add(rack)

        except Exception as e:
            log.error("Creating Datacenter: %s", e)
            db.session.rollback()

    for i in range(1, ITEM_MAX):
        item = Item()
        item.serial_number = serial_generator()
        item.model = get_random_name(models)
        db.session.add(item)
        log.info(item)
        try:
            db.session.commit()
        except Exception as e:
            log.error("Creating Item: %s", e)
            db.session.rollback()


with app.app_context():
    upsert_test_data()
