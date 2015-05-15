from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, String


class MyUser(User):
    '''
            MyUser fields
    '''
    domain = Column(String(32))
    group  = Column(String(32))

