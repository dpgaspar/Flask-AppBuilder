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
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    entry_points={'console_scripts': [
          'fabmanager = flask_appbuilder.console:cli',
      ]},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'colorama==0.3.9',
        'click==6.7',
        'Flask>=0.10.0,<0.12.99',
        'Flask-Babel==0.11.1',  # known issues with 0.11.2
        'Flask-Login==0.2.11',
        'Flask-OpenID==1.2.5',
        'Flask-SQLAlchemy==2.1',
        'Flask-WTF==0.14.2',
        'python-dateutil>=2.3, <3',
    ],
    tests_require=[
        'nose>=1.0',
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
