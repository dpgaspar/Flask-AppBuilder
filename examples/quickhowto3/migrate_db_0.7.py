import sys
import logging

from flask import Flask
from sqlalchemy import create_engine

from flask_appbuilder.security.sqla.models import User


logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger('Database Migration to 0.7')

try:
    app = Flask(__name__)
    app.config.from_object('config')

except Exception as e:

    if len(sys.argv) < 2:
        print "Without typical app structure use parameter to config"
        print "Use example for sqlite: python migrate_db_0.7.py sqlite:////home/user/application/app.db"
        exit()
    con_str = sys.argv[1]
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str


add_column_stmt = {'mysql': 'ALTER TABLE %s ADD COLUMN %s %s',
                   'sqlite': 'ALTER TABLE %s ADD COLUMN %s %s',
                   'postgresql': 'ALTER TABLE %s ADD COLUMN %s %s'}

mod_column_stmt = {'mysql': 'ALTER TABLE %s MODIFY COLUMN %s %s',
                   'sqlite': '',
                   'postgresql': 'ALTER TABLE %s ALTER COLUMN %s TYPE %s'}


def check_engine_support(conn):
    if not conn.engine.name in add_column_stmt:
        log.error('Engine type not supported by migration script, please alter schema for 0.7 read the documentation')
        exit()

def add_column(conn, table, column):
    table_name = table.__tablename__
    column_name = column.key
    column_type = column.type.compile(conn.dialect)
    try:
        log.info("Going to alter Column {0} on {1}".format(column_name, table_name))
        conn.execute(add_column_stmt[conn.engine.name] % (table_name, column_name, column_type))
        log.info("Added Column {0} on {1}".format(column_name, table_name))
    except Exception as e:
        log.error("Error adding Column {0} on {1}: {2}".format(column_name, table_name, str(e)))


def alter_column(conn, table, column):
    table_name = table.__tablename__
    column_name = column.key
    column_type = column.type.compile(conn.dialect)

    log.info("Going to alter Column {0} on {1}".format(column_name, table_name))
    try:
        conn.execute(mod_column_stmt[conn.engine.name] % (table_name, column_name, column_type))
        log.info("Altered Column {0} on {1}".format(column_name, table_name))
    except Exception as e:
        log.error("Error altering Column {0} on {1}: {2}".format(column_name, table_name, str(e)))


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
conn = engine.connect()
log.info("Database identified has {0}".format(conn.engine.name))
check_engine_support(conn)

alter_column(conn, User, User.password)
add_column(conn, User, User.login_count)
add_column(conn, User, User.created_on)
add_column(conn, User, User.changed_on)
add_column(conn, User, User.created_by_fk)
add_column(conn, User, User.changed_by_fk)
add_column(conn, User, User.last_login)
add_column(conn, User, User.fail_login_count)

conn.close()
