"""
    Console utility to help manage F.A.B's apps

    use it using fabmanager:

    $ fabmanager --help
"""

import click
import os
import sys
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen


def import_application(app_package, appbuilder):
    try:
        sys.path.append(os.getcwd())
        _app = __import__(app_package)
        return getattr(_app, appbuilder)
    except:
        click.echo(click.style('Was unable to import {0}.{1}'.format(app_package, appbuilder), fg='red'))
        exit(3)

@click.group()
def cli_app():
    """
        This is a set of commands to ease the creation and maintenance
        of your flask-appbuilder applications.
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
    _appbuilder = import_application(app, appbuilder)
    role_admin = _appbuilder.sm.find_role(_appbuilder.sm.auth_role_admin)
    _appbuilder.sm.add_user(username, firstname, lastname, email, role_admin, password)
    click.echo(click.style('Admin User {0} created.'.format(username), fg='green'))


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
        Flask-AppBuilder package version
    """
    _appbuilder = import_application(app, appbuilder)
    _appbuilder.security_cleanup()
    click.echo(click.style('Finished security cleanup', fg='green'))


@cli_app.command("list-views")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def list_users(app, appbuilder):
    """
        Flask-AppBuilder package version
    """
    _appbuilder = import_application(app, appbuilder)
    for view in _appbuilder.baseviews:
        click.echo('{0} : {1}'.format(view, view.route_base))


@cli_app.command("list-users")
@click.option('--app', default='app', help='Your application init directory (package)')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def list_users(app, appbuilder):
    """
        Flask-AppBuilder package version
    """
    _appbuilder = import_application(app, appbuilder)
    for user in _appbuilder.sm.get_all_users():
        click.echo(user)


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
def create_app(name):
    """
        Create a Skeleton application
    """
    try:
        url = urlopen("https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/archive/master.zip")
        zipfile = ZipFile(StringIO(url.read()))
        zipfile.extractall()
        os.rename("Flask-AppBuilder-Skeleton-master", name)
        click.echo(click.style('Downloaded the skeleton app, good coding!', fg='green'))
    except:
        click.echo(click.style('Something went wrong', fg='red'))
        click.echo(click.style('Try downloading from https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/archive/master.zip', fg='green'))

def cli():
    cli_app()

if __name__ == '__main__':
    cli_app()
