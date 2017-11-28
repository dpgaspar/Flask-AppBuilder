from app import db
from app.models import ContactGroup

db.create_all()

try:
    db.session.add(ContactGroup(name='Friends'))
    db.session.add(ContactGroup(name='Family'))
    db.session.add(ContactGroup(name='Work'))
    db.session.commit()
except:
    db.session.rollback()
