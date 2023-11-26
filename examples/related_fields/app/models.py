import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

mindate = datetime.date(datetime.MINYEAR, 1, 1)


class ContactGroup(Model):
    __tablename__ = "contact_group"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ContactGroup2(Model):
    __tablename__ = "contact_group2"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ContactSubGroup2(Model):
    __tablename__ = "contact_sub_group2"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    contact_group2_id = Column(Integer, ForeignKey("contact_group2.id"), nullable=False)
    contact_group2 = relationship("ContactGroup2")

    def __repr__(self):
        return self.name


class ContactSubGroup(Model):
    __tablename__ = "contact_sub_group"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    contact_group_id = Column(Integer, ForeignKey("contact_group.id"), nullable=False)
    contact_group = relationship("ContactGroup")

    def __repr__(self):
        return self.name


class Gender(Model):
    __tablename__ = "gender"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Contact(Model):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey("contact_group.id"), nullable=False)
    contact_group = relationship("ContactGroup")
    contact_sub_group_id = Column(
        Integer, ForeignKey("contact_sub_group.id"), nullable=False
    )
    contact_sub_group = relationship("ContactSubGroup")

    contact_group2_id = Column(Integer, ForeignKey("contact_group2.id"))
    contact_group2 = relationship("ContactGroup2")
    contact_sub_group2_id = Column(Integer, ForeignKey("contact_sub_group2.id"))
    contact_sub_group2 = relationship("ContactSubGroup2")

    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False)
    gender = relationship("Gender")

    def __repr__(self):
        return self.name

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)
