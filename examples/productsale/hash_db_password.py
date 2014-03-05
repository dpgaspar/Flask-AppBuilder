import sys
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from app import db
    from flask_appbuilder.security.models import User
except:
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    con_str = sys.argv[1]
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str
    db = SQLAlchemy(app)


try:
    users = db.session.query(User).all()
except:
    print "Query, connection error {}".format(sys.exc_info()[0])
    print "Config db key {}".format(app.config['SQLALCHEMY_DATABASE_URI'])
    exit()

for user in users:
    print "Hashing password for {}".format(user.full_name)
    user.password = generate_password_hash(user.password)
    try:
        db.session.merge(user)
        db.session.commit()
    except:
        print "Error updating password for {}".format(user.full_name)

