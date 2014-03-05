import sys

try:
    from app import db
    from flask_appbuilder.security.models import User
except:
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    con_str = sys.argv[0]
    app = Flask(__name__)
    app.config.['SQLALCHEMY_DATABASE_URI'] = con_str
    db = SQLAlchemy(app)


try:
    users = db.session.query(User).all()
except:
    print "Query, connection error"


for user in users:
    print "Hashing password for {}".format(user.full_name)

