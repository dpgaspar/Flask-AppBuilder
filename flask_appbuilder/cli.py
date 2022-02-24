from io import BytesIO
import os
import shutil
from typing import Optional, Union
from urllib.request import urlopen
from zipfile import ZipFile

import click
from flask import current_app
from flask.cli import with_appcontext

from .const import AUTH_DB, AUTH_LDAP, AUTH_OAUTH, AUTH_OID, AUTH_REMOTE_USER


SQLA_REPO_URL = (
    "https://github.com/dpgaspar/Flask-AppBuilder-Skeleton/archive/master.zip"
)
MONGOENGIE_REPO_URL = (
    "https://github.com/dpgaspar/Flask-AppBuilder-Skeleton-me/archive/master.zip"
)
ADDON_REPO_URL = (
    "https://github.com/dpgaspar/Flask-AppBuilder-Skeleton-AddOn/archive/master.zip"
)


def echo_header(title):
    click.echo(click.style(title, fg="green"))
    click.echo(click.style("-" * len(title), fg="green"))


def cast_int_like_to_int(cli_arg: Union[None, str, int]) -> Union[None, str, int]:
    """Cast int-like objects to int if possible

    If the arg cannot be cast to an integer, return the unmodified object instead."""
    try:
        cli_arg_int = int(cli_arg)
        return cli_arg_int
    except TypeError:
        # Don't cast if None
        return cli_arg
    except ValueError:
        # Don't cast non-int-like strings
        return cli_arg


@click.group()
def fab():
    """ FAB flask group commands"""
    pass


@fab.command("create-admin")
@click.option("--username", default="admin", prompt="Username")
@click.option("--firstname", default="admin", prompt="User first name")
@click.option("--lastname", default="user", prompt="User last name")
@click.option("--email", default="admin@fab.org", prompt="Email")
@click.password_option()
@with_appcontext
def create_admin(username, firstname, lastname, email, password):
    """
        Creates an admin user
    """
    auth_type = {
        AUTH_DB: "Database Authentications",
        AUTH_OID: "OpenID Authentication",
        AUTH_LDAP: "LDAP Authentication",
        AUTH_REMOTE_USER: "WebServer REMOTE_USER Authentication",
        AUTH_OAUTH: "OAuth Authentication",
    }
    click.echo(
        click.style(
            "Recognized {0}.".format(
                auth_type.get(current_app.appbuilder.sm.auth_type, "No Auth method")
            ),
            fg="green",
        )
    )
    user = current_app.appbuilder.sm.find_user(username=username)
    if user:
        click.echo(click.style(f"Error! User already exists {username}", fg="red"))
        return
    user = current_app.appbuilder.sm.find_user(email=email)
    if user:
        click.echo(click.style(f"Error! User already exists {username}", fg="red"))
        return
    role_admin = current_app.appbuilder.sm.find_role(
        current_app.appbuilder.sm.auth_role_admin
    )
    user = current_app.appbuilder.sm.add_user(
        username, firstname, lastname, email, role_admin, password
    )
    if user:
        click.echo(click.style("Admin User {0} created.".format(username), fg="green"))
    else:
        click.echo(click.style("No user created an error occured", fg="red"))


@fab.command("create-user")
@click.option("--role", default="Public", prompt="Role")
@click.option("--username", prompt="Username")
@click.option("--firstname", prompt="User first name")
@click.option("--lastname", prompt="User last name")
@click.option("--email", prompt="Email")
@click.password_option()
@with_appcontext
def create_user(role, username, firstname, lastname, email, password):
    """
        Create a user
    """
    user = current_app.appbuilder.sm.find_user(username=username)
    if user:
        click.echo(click.style(f"Error! User already exists {username}", fg="red"))
        return
    user = current_app.appbuilder.sm.find_user(email=email)
    if user:
        click.echo(click.style(f"Error! User already exists {username}", fg="red"))
        return
    role_object = current_app.appbuilder.sm.find_role(role)
    if not role_object:
        click.echo(click.style(f"Error! Role not found {role}", fg="red"))
        return
    user = current_app.appbuilder.sm.add_user(
        username, firstname, lastname, email, role_object, password
    )
    if user:
        click.echo(click.style("User {0} created.".format(username), fg="green"))
    else:
        click.echo(click.style("Error! No user created", fg="red"))


@fab.command("reset-password")
@click.option(
    "--username",
    default="admin",
    prompt="The username",
    help="Resets the password for a particular user.",
)
@click.password_option()
@with_appcontext
def reset_password(username, password):
    """
        Resets a user's password
    """
    user = current_app.appbuilder.sm.find_user(username=username)
    if not user:
        click.echo("User {0} not found.".format(username))
    else:
        current_app.appbuilder.sm.reset_password(user.id, password)
        click.echo(click.style("User {0} reseted.".format(username), fg="green"))


@fab.command("create-db")
@with_appcontext
def create_db():
    """
        Create all your database objects (SQLAlchemy specific).
    """
    from flask_appbuilder.models.sqla import Model

    engine = current_app.appbuilder.get_session.get_bind(mapper=None, clause=None)
    Model.metadata.create_all(engine)
    click.echo(click.style("DB objects created", fg="green"))


@fab.command("export-roles")
@with_appcontext
@click.option("--path", "-path", help="Specify filepath to export roles to")
@click.option("--indent", help="Specify indent of generated JSON file")
def export_roles(
    path: Optional[str] = None, indent: Optional[Union[int, str]] = None
) -> None:
    """Exports roles with permissions and view menus to JSON file"""
    # Cast negative numbers to int (as they are passed as str from CLI)
    cast_indent = cast_int_like_to_int(indent)
    current_app.appbuilder.sm.export_roles(path=path, indent=cast_indent)


@fab.command("import-roles")
@with_appcontext
@click.option(
    "--path", "-p", help="Path to a JSON file containing roles", required=True
)
def import_roles(path: str) -> None:
    """ Imports roles with permissions and view menus from JSON file """
    current_app.appbuilder.sm.import_roles(path)


@fab.command("version")
@with_appcontext
def version():
    """
        Flask-AppBuilder package version
    """
    click.echo(
        click.style(
            "F.A.B Version: {0}.".format(current_app.appbuilder.version),
            bg="blue",
            fg="white",
        )
    )


@fab.command("security-cleanup")
@with_appcontext
def security_cleanup():
    """
        Cleanup unused permissions from views and roles.
    """
    current_app.appbuilder.security_cleanup()
    click.echo(click.style("Finished security cleanup", fg="green"))


@fab.command("security-converge")
@click.option(
    "--dry-run", "-d", is_flag=True, help="Dry run & print state transitions."
)
@with_appcontext
def security_converge(dry_run=False):
    """
        Converges security deletes previous_class_permission_name
    """
    state_transitions = current_app.appbuilder.security_converge(dry=dry_run)
    if dry_run:
        click.echo(click.style("Computed security converge:", fg="green"))
        click.echo(click.style("Add to Roles:", fg="green"))
        for _from, _to in state_transitions["add"].items():
            click.echo(f"Where {_from} add {_to}")
        click.echo(click.style("Del from Roles:", fg="green"))
        for pvm in state_transitions["del_role_pvm"]:
            click.echo(pvm)
        click.echo(click.style("Remove views:", fg="green"))
        for views in state_transitions["del_views"]:
            click.echo(views)
        click.echo(click.style("Remove permissions:", fg="green"))
        for perms in state_transitions["del_perms"]:
            click.echo(perms)
    else:
        click.echo(click.style("Finished security converge", fg="green"))


@fab.command("create-permissions")
@with_appcontext
def create_permissions():
    """
        Creates all permissions and add them to the ADMIN Role.
    """
    current_app.appbuilder.add_permissions(update_perms=True)
    click.echo(click.style("Created all permissions", fg="green"))


@fab.command("list-views")
@with_appcontext
def list_views():
    """
        List all registered views
    """
    echo_header("List of registered views")
    for view in current_app.appbuilder.baseviews:
        click.echo(
            "View:{0} | Route:{1} | Perms:{2}".format(
                view.__class__.__name__, view.route_base, view.base_permissions
            )
        )


@fab.command("list-users")
@with_appcontext
def list_users():
    """
        List all users on the database
    """
    echo_header("List of users")
    for user in current_app.appbuilder.sm.get_all_users():
        click.echo(
            "username:{0} | email:{1} | role:{2}".format(
                user.username, user.email, user.roles
            )
        )


@fab.command("create-app")
@click.option(
    "--name",
    prompt="Your new app name",
    help="Your application name, directory will have this name",
)
@click.option(
    "--engine",
    prompt="Your engine type, SQLAlchemy or MongoEngine",
    type=click.Choice(["SQLAlchemy", "MongoEngine"]),
    default="SQLAlchemy",
    help="Write your engine type",
)
def create_app(name, engine):
    """
        Create a Skeleton application (needs internet connection to github)
    """
    try:
        if engine.lower() == "sqlalchemy":
            url = urlopen(SQLA_REPO_URL)
            dirname = "Flask-AppBuilder-Skeleton-master"
        elif engine.lower() == "mongoengine":
            url = urlopen(MONGOENGIE_REPO_URL)
            dirname = "Flask-AppBuilder-Skeleton-me-master"
        zipfile = ZipFile(BytesIO(url.read()))
        zipfile.extractall()
        os.rename(dirname, name)
        click.echo(click.style("Downloaded the skeleton app, good coding!", fg="green"))
        return True
    except Exception as e:
        click.echo(click.style("Something went wrong {0}".format(e), fg="red"))
        if engine.lower() == "sqlalchemy":
            click.echo(
                click.style(
                    "Try downloading from {0}".format(SQLA_REPO_URL), fg="green"
                )
            )
        elif engine.lower() == "mongoengine":
            click.echo(
                click.style(
                    "Try downloading from {0}".format(MONGOENGIE_REPO_URL), fg="green"
                )
            )
        return False


@fab.command("create-addon")
@click.option(
    "--name",
    prompt="Your new addon name",
    help="Your addon name will be prefixed by fab_addon_, directory will have this name",
)
def create_addon(name):
    """
        Create a Skeleton AddOn (needs internet connection to github)
    """
    try:
        full_name = "fab_addon_" + name
        dirname = "Flask-AppBuilder-Skeleton-AddOn-master"
        url = urlopen(ADDON_REPO_URL)
        zipfile = ZipFile(BytesIO(url.read()))
        zipfile.extractall()
        os.rename(dirname, full_name)
        addon_path = os.path.join(full_name, full_name)
        os.rename(os.path.join(full_name, "fab_addon"), addon_path)
        f = open(os.path.join(full_name, "config.py"), "w")
        f.write("ADDON_NAME='" + name + "'\n")
        f.write("FULL_ADDON_NAME='fab_addon_' + ADDON_NAME\n")
        f.close()
        click.echo(
            click.style("Downloaded the skeleton addon, good coding!", fg="green")
        )
        return True
    except Exception as e:
        click.echo(click.style("Something went wrong {0}".format(e), fg="red"))
        return False


@fab.command("collect-static")
@click.option(
    "--static_folder", default="app/static", help="Your projects static folder"
)
def collect_static(static_folder):
    """
        Copies flask-appbuilder static files to your projects static folder
    """
    appbuilder_static_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static/appbuilder"
    )
    app_static_path = os.path.join(os.getcwd(), static_folder)
    if not os.path.isdir(app_static_path):
        click.echo(
            click.style(
                "Static folder does not exist creating: %s" % app_static_path,
                fg="green",
            )
        )
        os.makedirs(app_static_path)
    try:
        shutil.copytree(
            appbuilder_static_path, os.path.join(app_static_path, "appbuilder")
        )
    except Exception:
        click.echo(
            click.style(
                "Appbuilder static folder already exists on your project", fg="red"
            )
        )


@fab.command("babel-extract")
@click.option("--config", default="./babel/babel.cfg")
@click.option("--input", default=".")
@click.option("--output", default="./babel/messages.pot")
@click.option("--target", default="app/translations")
@click.option(
    "--keywords", "-k", multiple=True, default=["lazy_gettext", "gettext", "_", "__"]
)
def babel_extract(config, input, output, target, keywords):
    """
        Babel, Extracts and updates all messages marked for translation
    """
    click.echo(
        click.style(
            "Starting Extractions config:{0} input:{1} output:{2} keywords:{3}".format(
                config, input, output, keywords
            ),
            fg="green",
        )
    )
    keywords = " -k ".join(keywords)
    os.popen(
        "pybabel extract -F {0} -k {1} -o {2} {3}".format(
            config, keywords, output, input
        )
    )
    click.echo(click.style("Starting Update target:{0}".format(target), fg="green"))
    os.popen("pybabel update -N -i {0} -d {1}".format(output, target))
    click.echo(click.style("Finish, you can start your translations", fg="green"))


@fab.command("babel-compile")
@click.option(
    "--target",
    default="app/translations",
    help="The target directory where translations reside",
)
def babel_compile(target):
    """
        Babel, Compiles all translations
    """
    click.echo(click.style("Starting Compile target:{0}".format(target), fg="green"))
    os.popen("pybabel compile -f -d {0}".format(target))
