Flask App Builder
=================

Simple and rapid Application builder, built on top of `Flask <http://flask.pocoo.org/>`_.
includes detailed security, auto form generation, google charts and much more.

Take a look at instalation, quick how to tutorials, API reference etc:

`Documentation <http://flask-appbuilder.readthedocs.org/en/latest/>`_

Package Version
---------------

New 0.4.0 with some great new features ;)  

please read the `Versions <http://flask-appbuilder.readthedocs.org/en/latest/versions.html>`_


Includes:
---------

  - Security
        - Auto permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
        - Inserts on the Database all the detailed permissions possible on your application.
        - Public (no authentication needed) and Private permissions.
        - Role based permissions.
        - Authentication based on OpenID and Database (Planning LDAP).
  - Views and Widgets
	- Auto menu generator.
	- Various view widgets: lists, master-detail, list of thumbnails etc
	- Select2, Datepicker, DateTimePicker
	- Menu with icons
	- Google charts with automatic group by.
  - Forms
	- Auto Create, Remove, Add, Edit and Show from Database Models
	- Labels and descriptions for each field
	- Image and File support for upload and database field association. It will handle everything for you.
	- Field sets for Form's (Django style).
  - i18n
	- Support for multi-language via Babel (still not working in package form)
  - Bootstrap 3.0.0 CSS and js, with Select2 and DatePicker


Some pictures
-------------

`Login page (with AUTH_DB): <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login.png>`_

Lists:

`List contacts example <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png>`_

`List Group example with search <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png>`_

Charts:

`Group by pie chart <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart.png>`_

`Group by month chart <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png>`_

`Group by year chart <https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png>`_

Depends on:
-----------

- flask
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel


