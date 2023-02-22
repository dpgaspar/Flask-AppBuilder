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
        "apispec[yaml]>=3.3, <6",
        "colorama>=0.3.9, <1",
        "click>=8, <9",
        "email_validator>=1.0.5, <2",
        "Flask>=2, <3",
        "Flask-Babel>=1, <3",
        "Flask-Login>=0.3, <0.7",
        "Flask-SQLAlchemy>=2.4, <3",
        "Flask-WTF>=0.14.2, <2",
        "Flask-JWT-Extended>=4.0.0, <5.0.0",
        "jsonschema>=3, <5",
        "marshmallow>=3, <4",
        "marshmallow-enum>=1.5.1, <2",
        "marshmallow-sqlalchemy>=0.22.0, <0.27.0",
        "python-dateutil>=2.3, <3",
        "prison>=0.2.1, <1.0.0",
        "PyJWT>=2.0.0, <3.0.0",
        # Cautious cap
        "SQLAlchemy<1.5",
        "sqlalchemy-utils>=0.32.21, <1",
        "WTForms<4",
    ],
    extras_require={
        "jmespath": ["jmespath>=0.9.5"],
        "oauth": ["Authlib>=0.14, <2.0.0"],
        "openid": ["Flask-OpenID>=1.2.5, <2"],
    },
    tests_require=["nose>=1.0", "mockldap>=0.3.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires="~=3.7",
    test_suite="nose.collector",
)
