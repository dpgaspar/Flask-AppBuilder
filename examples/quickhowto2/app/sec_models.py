from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, ForeignKey, String, Sequence, Table
from sqlalchemy.orm import relationship, backref
from flask_appbuilder import Model

assoc_user_role = Table('ab_user_role', Model.metadata,
                                  Column('id', Integer, Sequence('seq_ab_user_role_pk'), primary_key=True),
                                  Column('user_id', Integer, ForeignKey('ab_user.id')),
                                  Column('role_id', Integer, ForeignKey('ab_role.id'))
)


class MyUser(User):
    extra = Column(String(256))
    roles = relationship('Role', secondary=assoc_user_role, backref='user')
