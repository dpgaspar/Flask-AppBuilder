Flask App Builder
=================

Simple and rapid application builder framework, built on top of `Flask <http://flask.pocoo.org/>`_.
includes detailed security, auto form generation, google charts and much more.

Take a look at installation, quick how to tutorials, API reference etc: `Documentation <http://flask-appbuilder.readthedocs.org/en/latest/>`_

Package Version
---------------

*New 0.7.0* with bug fixes, and new features. If your already using F.A.B. read carefully the `migration <http://flask-appbuilder.readthedocs.org/en/latest/versionmigration.html>`_ procedures.

Also read the `Versions <http://flask-appbuilder.readthedocs.org/en/latest/versions.html>`_ for further detail on what changed.

Fixes, Bugs and contributions
-----------------------------

You're welcome to report bugs, propose new features, or even better contribute to this project.

`Issues, bugs and new features <https://github.com/dpgaspar/Flask-AppBuilder/issues/new>`_

`Contribute <https://github.com/dpgaspar/Flask-AppBuilder/fork>`_

Includes:
---------

  - Security
      - Auto permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
      - Inserts on the Database all the detailed permissions possible on your application.
      - Public (no authentication needed) and Private permissions.
      - Role based permissions.
      - Authentication based on OpenID, Database and LDAP.
  - Views and Widgets
      - Auto menu generator.
      - Various view widgets: lists, master-detail, list of thumbnails etc
      - Select2, Datepicker, DateTimePicker
      - Menu with icons
      - Google charts with automatic group by.
  - Forms
      - Auto Create, Remove, Add, Edit and Show from Database Models
      - Labels and descriptions for each field.
      - Automatic base validators from model definition.
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


