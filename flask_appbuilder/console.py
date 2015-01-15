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

@cli.command("babel-extract")
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

@cli.command("babel-compile")
@click.option('--target', default='app/translations')
def babel_extract(target):
    """
        Babel, Compiles all translations
    """
    click.echo(click.style('Starting Compile target:{0}'.format(target), fg='green'))
    os.popen('pybabel compile -f -d {0}'.format(target))

@cli.command("version")
def version():
    """
        Flask-AppBuilder package version
    """
    click.echo(click.style('F.A.B Version: {0}.'.format(_appbuilder.version), bg='blue', fg='white'))



if __name__ == '__main__':
    cli()
