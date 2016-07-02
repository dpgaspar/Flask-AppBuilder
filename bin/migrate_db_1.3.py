import sys,os
import logging

from flask import Flask
from sqlalchemy import create_engine

from flask_appbuilder.security.sqla.models import User

sys.path.append(os.getcwd())
from flask_appbuilder import SQLA

#from app import app
#from app import appbuilder, db

logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger('Database Migration to 1.3')

if len(sys.argv) < 2:
    log.info("Without typical app structure use parameter to config")
    log.info("Use example for sqlite: python migrate_db_1.3.py sqlite:////home/user/application/app.db")
    exit()

con_str = sys.argv[1]
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = con_str
db = SQLA(app)

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

db.session.remove()
db.create_all()

conn.execute("INSERT INTO ab_user_role (user_id,role_id) SELECT id,role_id from ab_user")

if conn.engine.name == 'postgresql':
    sequenceremap={ 'seq_ab_permission_pk':'ab_permission_id_seq',
                    'seq_ab_view_menu_pk' :'ab_view_menu_id_seq',
                    'seq_permission_view_pk': 'ab_permission_view_id_seq',
                    'seq_ab_permission_view_role_pk': 'ab_permission_view_role_id_seq',
                    'seq_ab_role_pk rename': 'ab_role_id_seq',
                    'seq_ab_user_role_pk': 'ab_user_role_id_seq',
                    'seq_ab_user_pk': 'ab_user_id_seq',
                    'seq_ab_register_user_pk': 'ab_register_user_id_seq'
                }
                    
    for seq in sequenceremap.keys():
        checksequence=conn.execute("SELECT 0 from pg_class where relname=%s;", seq)
        if checksequence.fetchone() is not None:            
            conn.execute("alter sequence %s rename to %s;" % (seq,sequenceremap[seq]))
    



#alter_column(conn, User, User.password)
#add_column(conn, User, User.login_count)
#add_column(conn, User, User.created_on)
#add_column(conn, User, User.changed_on)
#add_column(conn, User, User.created_by_fk)
#add_column(conn, User, User.changed_by_fk)
#add_column(conn, User, User.last_login)
#add_column(conn, User, User.fail_login_count)

conn.close()
