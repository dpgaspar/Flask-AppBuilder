from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey


class Settings(Base):
    __tablename__ = 'ab_settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.key
