import logging
import sys

from werkzeug.security import generate_password_hash

from flask_appbuilder.security.sqla.models import User


try:
    from app import app, db

except:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    if len(sys.argv) < 2:
        print "Without typical app structure use parameter to config"
        print "Use example: python hash_db_password.py sqlite:////home/user/application/app.db"
        exit()
    con_str = sys.argv[1]
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str
    db = SQLAlchemy(app)


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


try:
    log.info("using connection string: {0}".format(app.config['SQLALCHEMY_DATABASE_URI']))
    users = db.session.query(User).all()
except Exception as e:
    log.error("Query, connection error {0}".format(e))
    log.error("Config db key {}".format(app.config['SQLALCHEMY_DATABASE_URI']))
    exit()

for user in users:
    log.info("Hashing password for {0}".format(user.username))
    user.password = generate_password_hash(user.password)
    try:
        db.session.merge(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error("Error updating password for {0}: {1}".format(user.full_name, str(e)))
        

