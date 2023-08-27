import subprocess

import click
from flask_appbuilder import __version__


CHANGELOG_TEMPLATE = """Improvements and Bug fixes on {version}
-----------------------------------

{changes}

"""

CHANGE_LOG_HEADER = """
Flask-AppBuilder ChangeLog
==========================
"""


def get_change_log_entries_for_rst(entries: str) -> str:
    # prefix every line with "-"
    return "\n".join(["- " + line for line in entries.split("\n")])


def write_change_log_entry(version: str, entries: str) -> None:
    with open("CHANGELOG.rst", "r") as f:
        content = f.read()
    changes_for_version = CHANGELOG_TEMPLATE.format(version=version, changes=entries)
    # add changes after changelog header
    content = (
        content[0 : len(CHANGE_LOG_HEADER)]
        + changes_for_version
        + content[len(CHANGE_LOG_HEADER) :]
    )
    with open("CHANGELOG.rst", "w") as f:
        f.write(content)


def write_new_version(old_version: str, new_version) -> None:
    with open("flask_appbuilder/__init__.py", "r") as f:
        content = f.read()
    content = content.replace(
        f'__version__ = "{old_version}"', f'__version__ = "{new_version}"'
    )
    with open("flask_appbuilder/__init__.py", "w") as f:
        f.write(content)


@click.command()
@click.option(
    "--version",
    prompt="this release version",
    required=True,
    help="A release version to create ex: 4.3.9rc1",
)
def create_release(version):
    """Create a release"""
    click.echo("Creating release changes")

    output = subprocess.check_output(
        f'git log --pretty=format:"%s [%an]" v{__version__}..master', shell=True
    )
    write_change_log_entry(
        version, get_change_log_entries_for_rst(output.decode("utf-8"))
    )
    write_new_version(__version__, version)


if __name__ == "__main__":
    create_release()
