import sys
import logging
from flask import Flask
from sqlalchemy import create_engine
from flask_appbuilder.security.models import User

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

try:
    app = Flask(__name__)
    app.config.from_object('config')

except Exception as e:
    from flask.ext.sqlalchemy import SQLAlchemy

    if len(sys.argv) < 2:
        print "Without typical app structure use parameter to config"
        print "Use example for sqlite: python migrate_db_0.7.py sqlite:////home/user/application/app.db"
        exit()
    con_str = sys.argv[1]
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str


def add_column(engine, table, column):
    table_name = table.__tablename__
    column_name = column.key
    column_type = column.type.compile(engine.dialect)
    try:
        log.info("Going to alter Column {0} on {1}".format(column_name, table_name))
        engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))
        log.info("Added Column {0} on {1}".format(column_name, table_name))
    except Exception as e:
        log.error("Error adding Column {0} on {1}: {2}".format(column_name, table_name, str(e)))

def alter_column(engine, table, column):
    table_name = table.__tablename__
    column_name = column.key
    column_type = column.type.compile(engine.dialect)
    try:
	log.info("Going to alter Column {0} on {1}".format(column_name, table_name))
        engine.execute('ALTER TABLE %s ALTER COLUMN %s TYPE %s' % (table_name, column_name, column_type))
        log.info("Altered Column {0} on {1}".format(column_name, table_name))
    except Exception as e:
        log.error("Error altering Column {0} on {1}: {2}".format(column_name, table_name, str(e)))

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
con = engine.connect()

alter_column(con, User, User.password)
add_column(con, User, User.login_count)
add_column(con, User, User.created_on)
add_column(con, User, User.changed_on)
add_column(con, User, User.created_by_fk)
add_column(con, User, User.changed_by_fk)
add_column(con, User, User.last_login)
add_column(con, User, User.fail_login_count)

con.close()
