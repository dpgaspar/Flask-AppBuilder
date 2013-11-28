Flask App Builder
=================
-----------------

New documentation at: http://flask-appbuilder.readthedocs.org/en/latest/

Simple and rapid Application builder, includes detailed security, auto form generation, google charts and much more.


Package Version
---------------

Finally 0.2.0 is out!!  please read the docs.

Improvements
------------

  - Pagination on lists.
  - Inline (panels) will reload/return to the same panel (via cookie).
  - Templates with url_for.
  - BaseApp injects all necessary filter in jinja2, no need to import.
  - New Chart type, group by month and year.
  - No need to define route_base on View Classes, will assume class name in lower case.
  - No need to define labels for model's columns, they will be prettified.
  - No need to define titles for list,add,edit and show views, they will be generated from the model's name.
  - No need to define menu url when registering a BaseView will be infered from BaseView.defaultview.

Bug Fixes
---------

  - OpenID pictures not showing.
  - Security reset password corrections.
  - Date null Widget correction.
  - list filter with text
  - Removed unnecessary keys from config.py on skeleton and examples.
  - Simple group by correction, when query does not use joined models.
  - Authentication with OpenID does not need reset password option.

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

Login page (with AUTH_DB):

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login.png "Login"

Lists:

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png

Charts:

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart.png

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png

https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png

Depends on:
-----------

- flask
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel

 
This is not production ready.

