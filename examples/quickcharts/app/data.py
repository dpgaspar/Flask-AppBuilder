import datetime
import logging
import random

from . import db
from .models import Country, CountryStats, PoliticalType

log = logging.getLogger(__name__)


def fill_data():
    countries = [
        "Portugal",
        "Germany",
        "Spain",
        "France",
        "USA",
        "China",
        "Russia",
        "Japan",
    ]
    politicals = ["Democratic", "Authorative"]
    for country in countries:
        c = Country(name=country)
        try:
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            log.error("Update ViewMenu error: %s", e)
            db.session.rollback()
    for political in politicals:
        c = PoliticalType(name=political)
        try:
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            log.error("Update ViewMenu error: %s", e)
            db.session.rollback()
    try:
        for x in range(1, 20):
            cs = CountryStats()
            cs.population = random.randint(1, 100)
            cs.unemployed = random.randint(1, 100)
            cs.college = random.randint(1, 100)
            year = random.choice(range(1900, 2012))
            month = random.choice(range(1, 12))
            day = random.choice(range(1, 28))
            cs.stat_date = datetime.datetime(year, month, day)
            cs.country_id = random.randint(1, len(countries))
            cs.political_type_id = random.randint(1, len(politicals))
            db.session.add(cs)
            db.session.commit()
    except Exception as e:
        log.error("Update ViewMenu error: %s", e)
        db.session.rollback()
