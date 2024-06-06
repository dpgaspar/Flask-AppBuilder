from flask_appbuilder.extensions import db
from sqlalchemy.exc import SQLAlchemyError

from .models import Gender


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
