Introduction
============

The main goal for this project is to provide a simple development framework that handles the main problems any web application or site encounters.

It's half way between a scaffolding package on Bootstrap 3 and a full development framework, it has some goodies built in like image and file handling on forms, and google charts

This will lower errors, bugs, project's time to deliver. It's intended to be a rapid application development tool.

This package has some CSS and JS batteries included:

	- Google charts CSS and JS
	- BootStrap CSS and JS
	- BootsWatch Themes
	- Font-Awesome CSS and Fonts

Includes
--------

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




