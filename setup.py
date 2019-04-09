import os
import sys
import imp
import multiprocessing
from setuptools import setup, find_packages


version = imp.load_source('version', os.path.join('flask_appbuilder', 'version.py'))

def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)

def read(fname):
    return open(fpath(fname)).read()

def desc():
    return read('README.rst')

setup(
    name='Flask-AppBuilder',
    version=version.VERSION_STRING,
    url='https://github.com/dpgaspar/flask-appbuilder/',
    license='BSD',
    author='Daniel Vaz Gaspar',
    author_email='danielvazgaspar@gmail.com',
    description='Simple and rapid application development framework, built on top of Flask. includes detailed security, auto CRUD generation for your models, google charts and much more.',
    long_description=desc(),
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    entry_points={'console_scripts': [
          'fabmanager = flask_appbuilder.console:cli',
      ]},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'colorama>=0.3.9,<1',
        'click>=6.7,<8',
        'apispec[yaml]>=1.1.1<2',
        'Flask>=0.12,<2',
        'Flask-Babel>=0.11.1,<1',
        'Flask-Login>=0.3,<0.5',
        'Flask-OpenID>=1.2.5,<2',
        'Flask-SQLAlchemy>=2.3,<3',
        'Flask-WTF>=0.14.2,<1',
        'Flask-JWT-Extended>=3.18,<4',
        'python-dateutil>=2.3,<3',
        'marshmallow>=2.18.0,<2.20',
        'marshmallow-enum>=1.4.1,<2',
        'marshmallow-sqlalchemy>=0.16.1<1',
        'prison==0.1.0',
        'jsonschema>=3.0.1<4',
        'PyJWT>=1.7.1'
    ],
    tests_require=[
        'nose>=1.0',
        'mockldap>=0.3.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='nose.collector'
)
