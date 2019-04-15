import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Country(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class PoliticalType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class CountryStats(Model):
    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, nullable=True)
    population = Column(Float)
    unemployed = Column(Float)
    college = Column(Float)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    country = relationship("Country")
    political_type_id = Column(Integer, ForeignKey("political_type.id"), nullable=False)
    political_type = relationship("PoliticalType")

    def __repr__(self):
        return "{0}:{1}:{2}:{3}".format(
            self.country, self.political_type, self.population, self.college
        )

    def month_year(self):
        return datetime.datetime(self.stat_date.year, self.stat_date.month, 1)

    def country_political(self):
        return str(self.country) + " - " + str(self.political_type)
