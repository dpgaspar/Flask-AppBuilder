# Fix for older setuptools
import re
import os

from setuptools import setup, find_packages


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    info = read('README.md')
    try:
        return info + '\n\n' + read('doc/changelog.rst')
    except IOError:
        return info

# grep flask_admin/__init__.py since python 3.x cannot import it before using 2to3
file_text = read(fpath('flask_appbuilder/__init__.py'))
def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


setup(
    name='Flask-AppBuilder',
    version=grep('__version__'),
    url='https://github.com/dpgaspar/flask-appbuilder/',
    license='BSD',
    author=grep('__author__'),
    author_email=grep('__email__'),
    description='Simple and rapid Application builder, includer detailed security, auto form generation, google charts and much more.',
    long_description=desc(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.7',
        'Flask-Babel==0.8',
        'Flask-Login>=0.1.2',
        'Flask-OpenID>=1.1.0',
        'Flask-SQLAlchemy==0.16',
        'Flask-WTF==0.8.3',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite=''
)
