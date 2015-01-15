"""
    Console utility to help manage F.A.B's apps

    use it using fabmanager:

    $ fabmanager --help
"""

import click
import os
import sys

_appbuilder = None

@click.group()
@click.option('--app', default='app', help='Your application init directory')
@click.option('--appbuilder', default='appbuilder', help='your AppBuilder object')
def cli(app, appbuilder):
    global _appbuilder
    sys.path.append(os.getcwd())
    _app = __import__(app)
    _appbuilder = getattr(_app, appbuilder)

@cli.command("resetpassword")
@click.option('--username', default='admin', prompt='The username', help='Resets the password for a particular user.')
@click.password_option()
def resetpassword(username, password):
    """
        Resets a user's password
    """
    user = _appbuilder.sm.find_user(username=username)
    if not user:
        click.echo('User {0} not found.'.format(username))
    else:
        _appbuilder.sm.reset_password(user.id, password)
        click.echo(click.style('User {0} reseted.'.format(username), fg='green'))

@cli.command("createadmin")
@click.option('--username', default='admin', prompt='Username')
@click.option('--firstname', default='admin', prompt='User first name')
@click.option('--lastname', default='user', prompt='User last name')
@click.option('--email', default='admin@fab.org', prompt='Email')
@click.password_option()
def createadmin(username, firstname, lastname, email, password):
    """
        Creates an admin user
    """
    role_admin = _appbuilder.sm.find_role(_appbuilder.sm.auth_role_admin)
    _appbuilder.sm.add_user(username, firstname, lastname, email, role_admin, password)
    click.echo(click.style('Admin User {0} created.'.format(username), fg='green'))

@cli.command("run")
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8080)
@click.option('--debug', default=True)
def run(host, port, debug):
    """
        Runs Flask dev web server.
    """
    _appbuilder.get_app.run(host=host, port=port, debug=debug)

@cli.command("version")
def version():
    """
        Flask-AppBuilder package version
    """
    click.echo(click.style('F.A.B Version: {0}.'.format(_appbuilder.version), bg='blue', fg='white'))



if __name__ == '__main__':
    cli()
