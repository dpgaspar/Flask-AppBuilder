from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, String


class MyUser(User):
    extra = Column(String(256))
