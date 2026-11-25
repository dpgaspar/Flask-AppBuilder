from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from .models import Gender


def fill_gender():
    try:
        current_app.appbuilder.session.add(Gender(name="Male"))
        current_app.appbuilder.session.add(Gender(name="Female"))
        current_app.appbuilder.session.commit()
    except SQLAlchemyError:
        current_app.appbuilder.session.rollback()
