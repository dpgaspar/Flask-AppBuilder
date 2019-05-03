Flask App Builder
=================

.. image:: https://travis-ci.org/dpgaspar/Flask-AppBuilder.png?branch=master
        :target: https://travis-ci.org/dpgaspar/Flask-AppBuilder

.. image:: https://img.shields.io/pypi/v/Flask-AppBuilder.svg
        :alt: PyPI
        :target: https://pypi.org/project/Flask-AppBuilder/

.. image:: https://img.shields.io/badge/pyversions-3.6%2C3.7-blue.svg
        :target: https://www.python.org/

.. image:: https://coveralls.io/repos/dpgaspar/Flask-AppBuilder/badge.png?branch=master
        :target: https://coveralls.io/r/dpgaspar/Flask-AppBuilder


Simple and rapid application development framework, built on top of `Flask <http://flask.pocoo.org/>`_.
includes detailed security, auto CRUD generation for your models, google charts and much more.

Extensive configuration of all functionality, easily integrate with normal Flask/Jinja2 development.

- Documentation: `Documentation <http://flask-appbuilder.readthedocs.org/en/latest/>`_

- Mailing list: `Google group <https://groups.google.com/forum/#!forum/flask-appbuilder>`_

- Chat: `Gitter <https://gitter.im/dpgaspar/Flask-AppBuilder>`_

- Examples: `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_

Checkout installation video on `YouTube <http://youtu.be/xvum4vfwldg>`_

Quick how to `Demo from the docs <http://flaskappbuilder.pythonanywhere.com/>`_ (login has guest/welcome).

Change Log
----------

`Versions <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/CHANGELOG.rst>`_ for further detail on what changed.

Since 2.0.0 that `fabmanager` command line is considered **deprecated**, use the new `flask fab <command>` instead

Fixes, Bugs and contributions
-----------------------------

You're welcome to report bugs, propose new features, or even better contribute to this project.

`Issues, bugs and new features <https://github.com/dpgaspar/Flask-AppBuilder/issues/new>`_

`Contribute <https://github.com/dpgaspar/Flask-AppBuilder/fork>`_

Projects/Organizations using FAB
--------------------------------

If you would like to share your project, or let everyone know that you're using FAB
on your organization please submit a PR or send me an email with the details.

Projects:

- `Superset <https://github.com/apache/incubator-superset>`_ - a data exploration platform designed to be visual, intuitive, and interactive

- `Airflow <https://github.com/apache/airflow>`_ - a platform to programmatically author, schedule, and monitor workflows.


Organizations:

- Miniclip
- EuroBIC
- `On Beat Digital <https://onbeat.digital/>`_

Includes:
---------

  - Database
      - SQLAlchemy, multiple database support: sqlite, MySQL, ORACLE, MSSQL, DB2 etc.
      - Partial support for MongoDB using MongoEngine.
      - Multiple database connections support (Vertical partitioning).
      - Easy mixin audit to models (created/changed by user, and timestamps).
  - Security
      - Automatic permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
      - Inserts on the Database all the detailed permissions possible on your application.
      - Public (no authentication needed) and Private permissions.
      - Role based permissions.
      - Authentication support for OAuth, OpenID, Database, LDAP and REMOTE_USER environ var.
      - Support for self user registration.
  - Views and Widgets
      - Automatic menu generation.
      - Automatic CRUD generation.
      - Multiple actions on db records.
      - Big variety of filters for your lists.
      - Various view widgets: lists, master-detail, list of thumbnails etc
      - Select2, Datepicker, DateTimePicker
      - Related Select2 fields.
      - Google charts with automatic group by or direct values and filters.
      - AddOn system, write your own and contribute.
  - CRUD REST API
      - Automatic CRUD RESTful APIs.
      - Internationalization
      - Integration with flask-jwt-extended extension to protect your endpoints.
      - Metadata for dynamic rendering.
      - Selectable columns and metadata keys.
      - Automatic and configurable data validation.
  - Forms
      - Automatic, Add, Edit and Show from Database Models
      - Labels and descriptions for each field.
      - Automatic base validators from model's definition.
      - Custom validators, extra fields, custom filters for related dropdown lists.
      - Image and File support for upload and database field association. It will handle everything for you.
      - Field sets for Form's (Django style).
  - i18n
      - Support for multi-language via Babel
  - Bootstrap 3.1.1 CSS and js, with Select2 and DatePicker
  - Font-Awesome icons, for menu icons and actions.


Some pictures
-------------

Login page (with AUTH_DB)

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png


Login page (with AUTH_OAUTH)

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oauth.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oauth.png


Security

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png


Lists:

List contacts example

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png


List Group example with search

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png



Charts:

Group by pie chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/grouped_chart.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/grouped_chart.png

Direct time chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/direct_chart.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png

Group by time chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png


Depends on:
-----------

- flask
- click
- colorama
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel
