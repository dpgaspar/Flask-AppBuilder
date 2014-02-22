Versions
========

Improvements and Bug fixes on 0.6.8
-----------------------------------

- Fix, LDAP server key was hardcoded.

Improvements and Bug fixes on 0.6.7
-----------------------------------

- New, LDAP Authentication type, tested on MS Active Directory.

Improvements and Bug fixes on 0.6.6
-----------------------------------

- New, automatic support for required field validation on related dropdown lists.
- Fix, does not allow empty passwords on user creation.
- Fix, does not allow a user without a role assigned.
- Fix, OpenID bug. Needs flask-openID > 1.2.0

Improvements and Bug fixes on 0.6.5
-----------------------------------

- Fix, allow to filter multiple related fields on forms. Support for Many to Many relations.

Improvements and Bug fixes on 0.6.4
-----------------------------------

- Field widget removed from forms module to new fieldwidgets, this can be a breaking feature.
- Form creation code reorg (more simple and readable).
- New, form db login with icons.
- New, No need to define menu url on chart views (when registering), will work like GeneralViews.
- New, related form field filter configuration, add_form_query_rel_fields and edit_form_query_rel_fields.

Improvements and Bug fixes on 0.6.3
-----------------------------------

- Fix, Add and edit form will not surpress fields if filters come from user search. will only surpress on related views behaviour.
- New, added pagination to list thumbnails.
- Fix, no need to have a config.py to configure key for image upload and file upload.
- New, new config key for resizing images, IMG_SIZE.

Improvements and Bug fixes on 0.6.2
-----------------------------------

- New, compact view with add and edit on the same page has lists. Use of CompactCRUDMixin Mixin.
- Break, GeneralView (BaseCRUDView) related_views attr, must be filled with classes intead of instances.
- Fix, removed Flask-SQlAlchemy version constraint.
- Fix, TimeChartView resolved error with null dates. 
- Fix, registering related_views with instances will raise proper error.
- Fix, filter not supported with report a warning not an error.
- Fix, ImageColumn and FileColumn was being included has a possible filter.

Improvements and Bug fixes on 0.5.7
-----------------------------------

- New, package using python's logging module for correct and flexible logging of info and errors.

Improvements and Bug fixes on 0.5.6
-----------------------------------

- Fix, list_block, list_thumbnail, list_item, bug on set_link_filter.

Improvements and Bug fixes on 0.5.5
-----------------------------------

- New, group by on time charts returns month name and year.
- Fix, better redirect, example: after delete, previous search will be preserved.
- New, widgets module reorg.
- Fix, add and edit with filter was not remving filtered columns, with auto fill.

Improvements and Bug fixes on 0.5.4
-----------------------------------

- Fix, missing import on baseviews, flask.request

Improvements and Bug fixes on 0.5.3
-----------------------------------

- Fix, security.manager api improvement.
- New, property for default order list on GeneralView.
- Fix, actions not permitted will not show on UI.
- Fix, BaseView, BaseModelView, BaseCRUDView separation to module baseviews.
- Fix, Flask-SQlAlchemy requirement version block removed.

Improvements and Bug fixes on 0.5.2
-----------------------------------

- Fix, Auto remove of non existent permissions from database and remove permissions from roles.

Improvements and Bug fixes on 0.5.1
-----------------------------------

- New, top menu support, no need to create category with submenus.
- New, reverse flag for navbar on Menu property.
- New, update bootwatch.

Improvements and Bug fixes on 0.5.0
-----------------------------------

- fix, security userinfo without has_access decorator.
- fix, encoding on search widget (List users breaks on portuguese).
- New, safe back button.
- fix, oid authentication failed.
- New, Change flask-babel to flask-babelpkg to support independent extension translations.
- fix, login forms with complete translations.
- New, actions on records use @action decorator.
- New, support for primary keys of any type.
- New, Font-Awesome included

Improvements and Bug fixes on 0.4.3
-----------------------------------

- New, Search (filter) with boolean types.
- New, Added search to users view.
- New, page size selection.
- New, filter Relation not equal to.

Improvements and Bug fixes on 0.4.1, 0.4.2
------------------------------------------

- Removed constraint in flask-login requirement for versions lower than 0.2.8, can be used 0.2.7 or lower and 0.2.9 and higher.
- fix, BaseCRUDView init properties correction.
- fix, delete user generates general error key.
- Changed default page_size to 10.

Improvements and Bug fixes on 0.4.0
-----------------------------------

- fix, page was "remenbered" by class, returned empty lists on queries and inline lists.
- New Filters class and BaseFilter with many subclasses. Restructing internals to enable feature.
- New UI for search widget, dynamic filters showing the possibilities from filters. Starts with, greater then, etc...
- New possible filters for dates, greater then, less, equal filters.
- Restructuring of query function, simplified.
- Internal class inherit change: BaseView, BaseModelView, BaseCRUDView, GeneralView.
- Internal class inherit change: BaseView, BaseModelView, BaseChartView, (ChartView|TimeChartView).
- Argument URL filter change "_flt_<index option filter>_<Col name>=<value>"
- New, no need to define search_columns property, if not defined all columns can be added to search.
- New, no need to define list_columns property, if not defined only the first orderable column will be displayed.
- New, no need to define order_columns property, if not defined all ordered columns will be defined.
- fix, class init properties correction
- New property base_filters to always filter the view, accepts functions and values with current filters
- Babel actualization for filters in spanish and portuguese

Improvements and Bug fixes on 0.3.17
------------------------------------

- fix, Redirect to login when access denied was broken.

Improvements and Bug fixes on 0.3.16
------------------------------------

- fix, Reset password form

Improvements and Bug fixes on 0.3.15
------------------------------------

- Html non compliance corrections
- Charts outside panel correction

Improvements and Bug fixes on 0.3.12
------------------------------------

- New property add_form_extra_fields to inject extra fields on add form
- New property edit_form_extra_fields to inject extra fields on edit form
- Add and edit form order correction, order in add_columns, edit_columns or fieldsets
- Correction of bootstrap inclusion

Improvements and Bug fixes on 0.3.11
------------------------------------

- Bootstrap css and js included in the package
- Jquery included in the package
- Google charts jsapi included in the package
- requirement and setup preventing install for flask-login 0.2.8 only 0.2.7 or earlier, bug on init.html

Improvements and Bug fixes on 0.3.10
------------------------------------

- New config key APP_ICON to include an image to the navbar.
- Removed "Home" on the menu
- New Widget for displaying lists of items ListItem (Widget)
- New widget for displaying lists on blocks thumbnails
- Logout translation on portuguese and spanish


Improvements and Bug fixes on 0.3.9
-----------------------------------

- Chart views with equal presentation has list views.
- Chart views with search possibility
- BaseMixin with automatic table name like flask-sqlalchemy, no need to use db.Model.
- Pre, Post methods to override, removes decorator classmethod

Improvements and Bug fixes on 0.3.0
-----------------------------------

- AUTH_ROLE_ADMIN, AUTH_ROLE_PUBLIC not required to be defined.
- UPLOAD_FOLDER, IMG_UPLOAD_FOLDER, IMG_UPLOAD_URL not required to be defined.
- AUTH_TYPE not required to be defined, will use default database auth
- Internal security changed, new internal class SecurityManager
- No need to use the base AppBuilder-Skeleton, removed direct import from app directory.
- No need to use init_app.py first run will create all tables and insert all necessary permissions.
- Auto migration from version 0.2.X to 0.3.X, because of security table names change.
- Babel translations for Spanish
- No need to initialize LoginManager, OID.
- No need to initialize Babel (Flask-Babel) (since 0.3.5).
- General import corrections
- Support for PostgreSQL


Improvements and Bug fixes on 0.2.0
-----------------------------------

- Pagination on lists.
- Inline (panels) will reload/return to the same panel (via cookie).
- Templates with url_for.
- BaseApp injects all necessary filter in jinja2, no need to import.
- New Chart type, group by month and year.
- No need to define route_base on View Classes, will assume class name in lower case.
- No need to define labels for model's columns, they will be prettified.
- No need to define titles for list,add,edit and show views, they will be generated from the model's name.
- No need to define menu url when registering a BaseView will be infered from BaseView.defaultview.
- OpenID pictures not showing.
- Security reset password corrections.
- Date null Widget correction.
- list filter with text
- Removed unnecessary keys from config.py on skeleton and examples.
- Simple group by correction, when query does not use joined models.
- Authentication with OpenID does not need reset password option.

