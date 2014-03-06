import sys
from werkzeug.security import generate_password_hash
from flask_appbuilder.security.models import User

try:
    from app import app, db

except:
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    if len(sys.argv) < 2:
        print "Without typical app structure use parameter to config"
        print "Use example: python hash_db_password.py sqlite:////home/user/application/app.db"
        exit()
    con_str = sys.argv[1]
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str
    db = SQLAlchemy(app)


try:
    print "using connection string: {0}".format(app.config['SQLALCHEMY_DATABASE_URI'])
    users = db.session.query(User).all()
except Exception as e:
    print "Query, connection error {0}".format(e)
    print "Config db key {}".format(app.config['SQLALCHEMY_DATABASE_URI'])
    exit()

for user in users:
    print "Hashing password for {0}".format(user.full_name)
    user.password = generate_password_hash(user.password)
    try:
        db.session.merge(user)
        db.session.commit()
    except:
        print "Error updating password for {0}".format(user.full_name)

