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
    try:
        engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))
        log.info("Added Column {0} on {1}".format(column_name, table_name))
    except Exception as e:
        log.error("Error adding Column {0} on {1}: {2}".format(column_name, table_name, str(e)))


engine = db.session.get_bind(mapper=None, clause=None)

add_column(engine, User, User.login_count)
add_column(engine, User, User.created_on)
add_column(engine, User, User.changed_on)
add_column(engine, User, User.created_by_fk)
add_column(engine, User, User.changed_by_fk)
add_column(engine, User, User.last_login)
add_column(engine, User, User.fail_login_count)
