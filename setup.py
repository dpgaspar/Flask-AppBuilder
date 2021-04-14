import io
import os
import re

from setuptools import find_packages, setup


with io.open("flask_appbuilder/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read("README.rst")


setup(
    name="Flask-AppBuilder",
    version=version,
    url="https://github.com/dpgaspar/flask-appbuilder/",
    license="BSD",
    author="Daniel Vaz Gaspar",
    author_email="danielvazgaspar@gmail.com",
    description=(
        "Simple and rapid application development framework, built on top of Flask."
        " includes detailed security, auto CRUD generation for your models,"
        " google charts and much more."
    ),
    long_description=desc(),
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    package_data={"": ["LICENSE"]},
    entry_points={
        "flask.commands": ["fab=flask_appbuilder.cli:fab"],
        "console_scripts": ["fabmanager = flask_appbuilder.console:cli"],
    },
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=[
        "apispec[yaml]>=3.3, <4",
        "colorama>=0.3.9, <1",
        "click>=6.7, <8",
        "email_validator>=1.0.5, <2",
        "Flask>=0.12, <2",
        "Flask-Babel>=1, <2",
        "Flask-Login>=0.3, <0.5",
        "Flask-OpenID>=1.2.5, <2",
        "Flask-SQLAlchemy>=2.4, <3",
        "Flask-WTF>=0.14.2, <0.15.0",
        "Flask-JWT-Extended>=3.18, <4",
        "jsonschema>=3.0.1, <4",
        "marshmallow>=3, <4",
        "marshmallow-enum>=1.5.1, <2",
        "marshmallow-sqlalchemy>=0.22.0, <0.24.0",
        "python-dateutil>=2.3, <3",
        "prison>=0.1.3, <1.0.0",
        "PyJWT>=1.7.1, <2.0.0",
        "sqlalchemy-utils>=0.32.21, <1",
    ],
    extras_require={"jmespath": ["jmespath>=0.9.5"]},
    tests_require=["nose>=1.0", "mockldap>=0.3.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires="~=3.6",
    test_suite="nose.collector",
)
