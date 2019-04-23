from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, String


class MyUser(User):
    __tablename__ = "ab_user"
    extra = Column(String(256))
