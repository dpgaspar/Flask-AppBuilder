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
        click.echo('User {0} reseted.'.format(username))

@cli.command("createadmin")
@click.option('--username', default='admin', prompt='The username')
@click.option('--firstname', default='admin', prompt='The username')
@click.option('--lastname', default='user', prompt='The username')
@click.option('--email', default='admin@fab.org', prompt='The username')
@click.password_option()
def createadmin(username, firstname, lastname, email, password):
    """
        Creates an admin user
    """
    role_admin = _appbuilder.sm.find_role(_appbuilder.sm.auth_role_admin)
    _appbuilder.sm.add_user(username, firstname, lastname, email, role_admin, password)
    click.echo('Admin User {0} created.'.format(username))


if __name__ == '__main__':
    cli()
