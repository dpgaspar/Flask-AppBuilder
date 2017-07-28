Introduction
============

The main goal for this project is to provide a simple development framework
that handles the main problems any web application or site encounters.
It will help you adhere to the DRY (Don't repeat yourself) principle.

Keep in mind that it is possible to develop directly on Flask/Jinja2 for custom pages or flows,
that painlessly integrate with the framework.

This framework goes further than an admin scaffolding package.
It has builtin presentation and behaviour alternatives, and you can easily build your own.
It's highly configurable, and ships with extra goodies.

It's intended to lower errors, bugs and project's time to deliver.

This package has some CSS and JS batteries included:

	- Google charts CSS and JS
	- BootStrap CSS and JS
	- BootsWatch Themes
	- Font-Awesome CSS and Fonts

-- Includes

  - Database
      - SQLAlchemy, multiple database support: sqlite, MySQL, ORACLE, MSSQL, DB2 etc.
      - MongoDB, using mongoEngine, still partial support (only normalized).
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
      - Various view widgets: lists, master-detail, list of thumbnails etc.
      - Select2, Datepicker, DateTimePicker.
      - Select2 related fields.
      - Google charts with automatic group by or direct values and filters.
  - Forms
      - Automatic, Add, Edit and Show from Database Models
      - Labels and descriptions for each field.
      - Automatic base validators from model's definition.
      - Custom validators, extra fields, custom filters for related dropdown lists.
      - Image and File support for upload and database field association. It will handle everything for you.
      - Field sets for Form's (Django style).
  - i18n
      - Support for multi-language via Babel.
  - Bootstrap 3.3.1 CSS and js, with Select2 and DatePicker.
  - Font-Awesome icons, for menu icons and actions.
  - Bootswatch Themes.



