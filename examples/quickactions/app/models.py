from sqlalchemy import Column, Integer, String
from flask_appbuilder import Model


class ContactGroup(Model):
    __tablename__ = "contact_group"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name
