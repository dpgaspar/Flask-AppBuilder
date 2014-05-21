Flask App Builder
=================

.. image:: https://travis-ci.org/dpgaspar/Flask-AppBuilder.png?branch=master
	:target: https://travis-ci.org/dpgaspar/Flask-AppBuilder
.. image:: https://pypip.in/version/Flask-AppBuilder/badge.png
	:target: https://pypi.python.org/pypi/Flask-AppBuilder
	:alt: Verion
.. image:: https://pypip.in/download/Flask-AppBuilder/badge.png
	:target: https://pypi.python.org/pypi/Flask-AppBuilder
	:alt: Downloads
.. image:: https://coveralls.io/repos/dpgaspar/Flask-AppBuilder/badge.png?branch=api-rework
    :target: https://coveralls.io/r/dpgaspar/Flask-AppBuilder?branch=api-rework

Simple and rapid application development framework, built on top of `Flask <http://flask.pocoo.org/>`_.
includes detailed security, auto CRUD generation for your models, google charts and much more.

Extensive configuration of all functionality, easily integrate with normal Flask/Jinja2 development.

Take a look at installation, quick how to tutorials, API reference etc: `Documentation <http://flask-appbuilder.readthedocs.org/en/latest/>`_

Lots of `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_ and a live quick how to `Demo from the docs <http://flaskappbuilder.pythonanywhere.com/>`_ (login has guest/welcome).

Package Version
---------------

*New 0.9.N* with an important fix to support non root url installations. New languages support.

If you're already using F.A.B. (0.8.N or earlier)
read carefully the `migration <http://flask-appbuilder.readthedocs.org/en/latest/versionmigration.html>`_ procedures.

Also read the `Versions <http://flask-appbuilder.readthedocs.org/en/latest/versions.html>`_ for further detail on what changed.

Fixes, Bugs and contributions
-----------------------------

You're welcome to report bugs, propose new features, or even better contribute to this project.

`Issues, bugs and new features <https://github.com/dpgaspar/Flask-AppBuilder/issues/new>`_

`Contribute <https://github.com/dpgaspar/Flask-AppBuilder/fork>`_

Includes:
---------

   - Database
      - SQLAlchemy, multiple database support: sqlite, MySQL, ORACLE, MSSQL, DB2 etc.
      - Multiple database connections support (Vertical partitioning).
      - Easy mixin audit to models (created/changed by user, and timestamps).
  - Security
      - Automatic permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
      - Inserts on the Database all the detailed permissions possible on your application.
      - Public (no authentication needed) and Private permissions.
      - Role based permissions.
      - Authentication support for OpenID, Database and LDAP.
  - Views and Widgets
      - Automatic menu generation.
      - Automatic CRUD generation.
      - Big variety of filters for your lists.
      - Various view widgets: lists, master-detail, list of thumbnails etc
      - Select2, Datepicker, DateTimePicker
      - Google charts with automatic group by or direct values and filters.
  - Forms
      - Automatic, Add, Edit and Show from Database Models
      - Labels and descriptions for each field.
      - Automatic base validators from model's definition.
      - Custom validators, extra fields, custom filters for related dropdown lists.
      - Image and File support for upload and database field association. It will handle everything for you.
      - Field sets for Form's (Django style).
  - i18n
      - Support for multi-language via Babel
  - Bootstrap 3.0.3 CSS and js, with Select2 and DatePicker
  - Font-Awesome icons, for menu icons and actions.


Some pictures
-------------

Login page (with AUTH_DB) 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png
    

Login page (with AUTH_OID)

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oid.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oid.png


Security 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png


Lists:

List contacts example 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png


`List Group example with search 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png


Charts:

Group by pie chart 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart.png

Group by month chart 

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png

Group by year chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png


Depends on:
-----------

- flask
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel


