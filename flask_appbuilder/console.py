"""
    Console utility to help manage F.A.B's apps

    use it using fabmanager:

    $ fabmanager --help
"""

import click
import os
import sys
from zipfile import ZipFile
from . import const as c

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
from io import BytesIO

SQLA_REPO_URL = 'https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/archive/master.zip'
MONGOENGIE_REPO_URL = 'https://github.com/dpgaspar/Flask-AppBuilder-Skeleton-me/archive/master.zip'

def import_application(app_package, appbuilder):
    sys.path.append(os.getcwd())
    try:
        _app = __import__(app_package)
    except Exception as e:
        click.echo(click.style('Was unable to import {0} Error: {1}'.format(app_package, e), fg='red'))
        exit(3)
    if hasattr(_app, 'appbuilder'):
        return getattr(_app, appbuilder)
    else:
        click.echo(click.style('There in no appbuilder var on your package, you can use appbuilder parameter to config', fg='red'))
        exit(3)


def echo_header(title):
    click.echo(click.style(title, fg='green'))
    click.echo(click.style('-'*len(title), fg='green'))


@click.group()
def cli_app():
    """
        This is a set of commands to ease the creation and maintenance
        of your flask-appbuilder applications.

        All commands that import your app will assume by default that
        your running on your projects directory just before the app directory.
        will assume also that on the __init__.py your initializing AppBuilder
        like this (using a var named appbuilder) just like the skeleton app::

        appbuilder = AppBuilder(......)

        If your using different namings use app and appbuilder parameters.
    """
    pass


@cli_app.command("reset-password")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
@click.option('--username', default='admin', prompt='The username', help='Resets the password for a particular user.')
@click.password_option()
def reset_password(app, appbuilder, username, password):
    """
        Resets a user's password
    """
    _appbuilder = import_application(app, appbuilder)
    user = _appbuilder.sm.find_user(username=username)
    if not user:
        click.echo('User {0} not found.'.format(username))
    else:
        _appbuilder.sm.reset_password(user.id, password)
        click.echo(click.style('User {0} reseted.'.format(username), fg='green'))

@cli_app.command("create-admin")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
@click.option('--username', default='admin', prompt='Username')
@click.option('--firstname', default='admin', prompt='User first name')
@click.option('--lastname', default='user', prompt='User last name')
@click.option('--email', default='admin@fab.org', prompt='Email')
@click.password_option()
def create_admin(app, appbuilder, username, firstname, lastname, email, password):
    """
        Creates an admin user
    """
    auth_type = {c.AUTH_DB:"Database Authentications",
                c.AUTH_OID:"OpenID Authentication",
                c.AUTH_LDAP:"LDAP Authentication",
                c.AUTH_REMOTE_USER:"WebServer REMOTE_USER Authentication",
                c.AUTH_OAUTH:"OAuth Authentication"}
    _appbuilder = import_application(app, appbuilder)
    click.echo(click.style('Recognized {0}.'.format(auth_type.get(_appbuilder.sm.auth_type,'No Auth method')), fg='green'))
    role_admin = _appbuilder.sm.find_role(_appbuilder.sm.auth_role_admin)
    user = _appbuilder.sm.add_user(username, firstname, lastname, email, role_admin, password)
    if user:
        click.echo(click.style('Admin User {0} created.'.format(username), fg='green'))
    else:
        click.echo(click.style('No user created an error occured', fg='red'))


@cli_app.command("run")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8080)
@click.option('--debug', default=True)
def run(app, appbuilder, host, port, debug):
    """
        Runs Flask dev web server.
    """
    _appbuilder = import_application(app, appbuilder)
    _appbuilder.get_app.run(host=host, port=port, debug=debug)


@cli_app.command("create-db")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def create_db(app, appbuilder):
    """
        Create all your database objects (SQLAlchemy specific).
    """
    from flask_appbuilder.models.sqla import Base

    _appbuilder = import_application(app, appbuilder)
    engine = _appbuilder.get_session.get_bind(mapper=None, clause=None)
    Base.metadata.create_all(engine)
    click.echo(click.style('DB objects created', fg='green'))


@cli_app.command("upgrade-db")
@click.option('--config', default='config', help='Your application config file path')
@click.option('--backup', default='no', prompt='Going to upgrade your DB to version 1.3.0, Did you backup your database?')
def upgrade_db(config, backup):
    """
        Upgrade your database after F.A.B. upgrade if necessary (SQLAlchemy only)

        Version 1.3.0 upgrade needs database upgrade, read version migration on docs for
        further details.
    """
    from flask import Flask
    from flask_appbuilder import SQLA
    from flask_appbuilder.security.sqla.models import User
    from sqlalchemy import Column, Integer, ForeignKey
    from sqlalchemy.orm import relationship


    class UpgProxyUser(User):
        role_id = Column(Integer, ForeignKey('ab_role.id'))
        role = relationship('Role')

    sequenceremap={ 'seq_ab_permission_pk':'ab_permission_id_seq',
                    'seq_ab_view_menu_pk' :'ab_view_menu_id_seq',
                    'seq_permission_view_pk': 'ab_permission_view_id_seq',
                    'seq_ab_permission_view_role_pk': 'ab_permission_view_role_id_seq',
                    'seq_ab_role_pk rename': 'ab_role_id_seq',
                    'seq_ab_user_role_pk': 'ab_user_role_id_seq',
                    'seq_ab_user_pk': 'ab_user_id_seq',
                    'seq_ab_register_user_pk': 'ab_register_user_id_seq'
                }

    del_column_stmt = {'mysql': 'ALTER TABLE %s DROP COLUMN %s',
                    'postgresql': 'ALTER TABLE %s DROP COLUMN %s',
                    'oracle': 'ALTER TABLE %s DROP COLUMN %s',
                    'mssql': 'ALTER TABLE %s DROP COLUMN %s'}

    del_foreign_stmt = {'mysql': 'ALTER TABLE %s DROP FOREIGN KEY %s',
                    'postgresql': 'ALTER TABLE %s DROP CONSTRAINT %s',
                    'oracle': 'ALTER TABLE %s DROP CONSTRAINT %s',
                    'mssql': 'ALTER TABLE %s DROP CONSTRAINT %s'}

    def del_column(conn, table_name, column_name):
        try:
            if conn.engine.name in del_column_stmt:
                click.echo(click.style("Going to delete Column {0} on {1}".format(column_name, table_name), fg='green'))
                conn.engine.execute(del_column_stmt[conn.engine.name] % (table_name, column_name))
                click.echo(click.style("Deleted Column {0} on {1}".format(column_name, table_name), fg='green'))
            else:
                click.echo(click.style("Engine {0} not supported for auto upgrade, del column {1}.{2} yourself" \
                                       .format(conn.engine.name, table_name, column_name), fg='red'))
        except Exception as e:
            click.echo(click.style("Error deleting Column {0} on {1}: {2}".format(column_name, table_name, str(e)), fg='red'))

    def del_foreign_key(conn, table_name, column_name):
        try:
            if conn.engine.name in del_foreign_stmt:
                click.echo(click.style("Going to drop FK {0} on {1}".format(column_name, table_name), fg='green'))
                conn.engine.execute(del_foreign_stmt[conn.engine.name] % (table_name, column_name))
                click.echo(click.style("Droped FK {0} on {1}".format(column_name, table_name), fg='green'))
            else:
                click.echo(click.style("Engine {0} not supported for auto upgrade, del FK {1}.{2} yourself" \
                                       .format(conn.engine.name, table_name, column_name), fg='red'))
        except Exception as e:
            click.echo(click.style("Error droping FK {0} on {1}: {2}".format(column_name, table_name, str(e)), fg='red'))


    if not backup.lower() in ('yes', 'y'):
        click.echo(click.style('Please backup first', fg='red'))
        exit(0)
    sys.path.append(os.getcwd())
    
    app = Flask(__name__)
    app.config.from_object(config)
    db = SQLA(app)
    db.create_all()

    # Upgrade Users append role on roles, allows 1.3.0 multiple roles for user.
    click.echo(click.style('Beginning user migration, hope you have backed up first', fg='green'))
    try:
        for user in db.session.query(UpgProxyUser).all():
            user.roles.append(user.role)
            db.session.commit()
            click.echo(click.style('Altered user {0}'.format(user.username), fg='green'))
    except:
            click.echo(click.style('Error on Upgrade, DB is probably already compliant', fg='green'))
            exit(0)
    db.session.remove()

    if db.engine.name == 'sqlite':
        click.echo(click.style('\n------------------\nTo finish the upgrade you must download and execute the following sql\n\
        Download from https://github.com/dpgaspar/Flask-AppBuilder/tree/master/bin/sqlite_upgrade_1.3.sql', fg='green'))
        exit(0)

    del_foreign_key(db, 'ab_user', 'ab_user_role_id_fkey')
    del_column(db, 'ab_user', 'role_id')
    
    # POSTGRESQL
    if db.engine.name == 'postgresql':
        for seq in sequenceremap.keys():
            try:
                checksequence=db.engine.execute("SELECT 0 from pg_class where relname=%s;", seq)
                if checksequence.fetchone() is not None:
                    db.engine.execute("alter sequence %s rename to %s;" % (seq, sequenceremap[seq]))
                click.echo(click.style('Altered sequence from {0} {1}'.format(seq,sequenceremap[seq]), fg='green'))
            except:
                click.echo(click.style('Error Altering sequence from {0} to {1}'.format(seq,sequenceremap[seq]), fg='red'))
    # ORACLE
    if db.engine.name == 'oracle':
        click.echo(click.style('Your using PostgreSQL going to change your sequence names', fg='green'))
        for seq in sequenceremap.keys():
            try:
                db.engine.execute("rename %s to %s;" % (seq, sequenceremap[seq]))
                click.echo(click.style('Altered sequence from {0} to {1}'.format(seq, sequenceremap[seq]), fg='green'))
            except:
                click.echo(click.style('Error Altering sequence from {0} to {1}'.format(seq, sequenceremap[seq]), fg='red'))


@cli_app.command("version")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def version(app, appbuilder):
    """
        Flask-AppBuilder package version
    """
    _appbuilder = import_application(app, appbuilder)
    click.echo(click.style('F.A.B Version: {0}.'.format(_appbuilder.version), bg='blue', fg='white'))


@cli_app.command("security-cleanup")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def security_cleanup(app, appbuilder):
    """
        Cleanup unused permissions from views and roles.
    """
    _appbuilder = import_application(app, appbuilder)
    _appbuilder.security_cleanup()
    click.echo(click.style('Finished security cleanup', fg='green'))


@cli_app.command("list-views")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def list_users(app, appbuilder):
    """
        List all registered views
    """
    _appbuilder = import_application(app, appbuilder)
    echo_header('List of registered views')
    for view in _appbuilder.baseviews:
        click.echo('View:{0} | Route:{1} | Perms:{2}'.format(view.__class__.__name__, view.route_base, view.base_permissions))


@cli_app.command("list-users")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def list_users(app, appbuilder):
    """
        List all users on the database 
    """
    _appbuilder = import_application(app, appbuilder)
    echo_header('List of users')
    for user in _appbuilder.sm.get_all_users():
        click.echo('username:{0} | email:{1} | role:{2}'.format(user.username, user.email, user.roles))


@cli_app.command("babel-extract")
@click.option('--config', default='./babel/babel.cfg')
@click.option('--input', default='.')
@click.option('--output', default='./babel/messages.pot')
@click.option('--target', default='app/translations')
def babel_extract(config, input, output, target):
    """
        Babel, Extracts and updates all messages marked for translation
    """
    click.echo(click.style('Starting Extractions config:{0} input:{1} output:{2}'.format(config, input, output), fg='green'))
    os.popen('pybabel extract -F {0} -k lazy_gettext -o {1} {2}'.format(config, output, input))
    click.echo(click.style('Starting Update target:{0}'.format(target), fg='green'))
    os.popen('pybabel update -N -i {0} -d {1}'.format(output, target))
    click.echo(click.style('Finish, you can start your translations', fg='green'))


@cli_app.command("babel-compile")
@click.option('--target', default='app/translations', help="The target directory where translations reside")
def babel_compile(target):
    """
        Babel, Compiles all translations
    """
    click.echo(click.style('Starting Compile target:{0}'.format(target), fg='green'))
    os.popen('pybabel compile -f -d {0}'.format(target))


@cli_app.command("create-app")
@click.option('--name', prompt="Your new app name", help="Your application name, directory will have this name")
@click.option('--engine', prompt="Your engine type, SQLAlchemy or MongoEngine", type=click.Choice(['SQLAlchemy', 'MongoEngine']),
              default='SQLAlchemy', help='Write your engine type')
def create_app(name, engine):
    """
        Create a Skeleton application (needs internet connection to github)
    """
    try:
        if engine.lower() =='sqlalchemy':
            url = urlopen(SQLA_REPO_URL)
            dirname = "Flask-AppBuilder-Skeleton-master"
        elif engine.lower() =='mongoengine':
            url = urlopen(MONGOENGIE_REPO_URL)
            dirname = "Flask-AppBuilder-Skeleton-me-master"
        zipfile = ZipFile(BytesIO(url.read()))
        zipfile.extractall()
        os.rename(dirname, name)
        click.echo(click.style('Downloaded the skeleton app, good coding!', fg='green'))
        return True
    except Exception as e:
        click.echo(click.style('Something went wrong {0}'.format(e), fg='red'))
        if engine.lower() =='sqlalchemy':
            click.echo(click.style('Try downloading from {0}'.format(SQLA_REPO_URL), fg='green'))
        elif engine.lower() =='mongoengine':
            click.echo(click.style('Try downloading from {0}'.format(MONGOENGIE_REPO_URL), fg='green'))
        return False

def cli():
    cli_app()

if __name__ == '__main__':
    cli_app()
