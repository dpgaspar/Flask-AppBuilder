import sys
import logging
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


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

def add_column(engine, table, column):
  table_name = table.__tablename__
  column_name = column.key
  column_type = column.type.compile(engine.dialect)
  engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))


engine = db.session.get_bind(mapper=None, clause=None)

add_column(engine, User, User.login_count)
