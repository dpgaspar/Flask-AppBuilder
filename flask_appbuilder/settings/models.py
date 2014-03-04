from sqlalchemy import Column, Integer, String, Boolean
from flask.ext.appbuilder import Base


class Setting(Base):
    __tablename__ = 'ab_setting'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(100), nullable=False)
    is_internal = Column(Boolean)

    def __repr__(self):
        return "{}:{}".format(self.key, self.value)

