Versions
========

Improvements and Bug fixes on 1.1.0
-----------------------------------

- Fix, changed WTForm validator Required to DataRequired.
- Fix, changed WTForm TextField to StringField.
- New, AUTH_USER_REGISTRATION for self user registration, on ldap it's used automatic registration based on ldap attrs.
- New, AUTH_USER_REGISTRATION for auth db will present registration form, send email with configurable html for activation.
- New, AUTH_USER_REGISTRATION for auth oid will present registration form, send email with configurable html for activation.
- New, Added property to AppBuilder that returns the frameworks version.
- New, User extension mixin (Beta).
- New, allows dotted attributes on list_columns, to fetch values from related models.
- New, AuthOIDView with oid_ask_for and oid_ask_for_optional, for easy dev override of view.
- New, Access Denied log a warning with info.
- Fix, OpenID login improvement.

Improvements and Bug fixes on 1.0.1
-----------------------------------

- Fix, field icon for date and datetime that selects calendar, changes mouse cursor to hand.
- New, render_field changed, could be a breaking feature, if you wrote your own forms. no more <td> on each field.
- New, pull request #44, ldap bind options.
- Fix, pull request #48, bug with back button url not working when using uwsgi under sub-domain.
- New, AppBuilder accepts new parameter security_manager_class, useful to override any security view or auth method.


Improvements and Bug fixes on 1.0.0
-----------------------------------

- New, dynamic package version from python file version.py.
- New, extra_args property, for injecting extra arguments to templates.
- Fix, Removed footer with link "Powered by F.A.B.".
- Fix, Added translation for "Access is denied". ES,GE,RU,ZH
- New, Yes and no questions with bootstrap modal.
- Fix, Added multiple actions support on other list widgets.
- Fix, missing translations for "User info" and "Audit info".

Improvements and Bug fixes on 0.10.7
------------------------------------

- Fix, actions break on MasterDetail or related views.

Improvements and Bug fixes on 0.10.6
------------------------------------

- New, Support for multiple actions.

Improvements and Bug fixes on 0.10.5
------------------------------------

- Fix, Russian translations from pull request #39

Improvements and Bug fixes on 0.10.4
------------------------------------

- Fix, merge problem. issue #38

Improvements and Bug fixes on 0.10.3
------------------------------------

- Fix, inserted script in init.html moved to ab.js on static/js.
- Fix, performance improvement on edit, only one form initialization.
- New, New back mechanism, with 5 history records. issue #35.
- New, json endpoint for model querys, with same parameters has list endpoint.
- New, support for boolean columns search, filter with FilterEqual or FilterNotEqual.

Improvements and Bug fixes on 0.10.2
------------------------------------

- Fix, get order columns was including relations.
- New, possibility to include primary key and foreign key on forms and views.
- Fix, python 3 errors on GenericModels, metaclass compatibility.

Improvements and Bug fixes on 0.10.1
------------------------------------

- New, decorator '@permission_name' to override endpoint access permission name.
- Fix, edit_form_query_rel_fields error only on 0.10.0, issue #30.
- Fix, only add permissions to methods with @has_access decorator.
- Fix, prevents duplicate permissions.

Improvements and Bug fixes on 0.10.0
------------------------------------

- New, template block on add.html template, add_form.
- New, template block on edit.html template, edit_form.
- New, template block on show.html template, show_form.
- New, template block on show_cascade.html template, relative_views.
- New, template block on edit_cascade.html template, relative_views.
- New, API Change, DataModel is now BaseInterface and on flask.ext.appbuilder.models.base
- New, API Change, SQLAModel is now SQLAInterface
- New, API Change, SQLAInterface inherits from BaseInterface (not DataModel)
- New, API Change, SQLAInterface is on flask.ext.appbuilder.models.sqla.interface
- New, API Change, Filters for sqla are on flask.ext.appbuilder.models.sqla.filters
- New, API Change, BaseFilter is on flask.ext.appbuilder.model.base
- Fix, nullable Float and Integer bug issue #26
- New, default model sqlalchemy support on forms (issue #26). static and callable value

Improvements and Bug fixes on 0.9.3
-----------------------------------

- Fix, DateTimeField Fix issue #22.
- New, bootstrap updated to version 3.1.1.
- New, fontawesome updated to version 4.1.0.

Improvements and Bug fixes on 0.9.2
-----------------------------------

- Fix, label for 'username' was displaying 'Failed Login Count', Chart definition override.

Improvements and Bug fixes on 0.9.1
-----------------------------------

- New, Support for application factory *init_app* (Flask ext approved guide line).
- New, Flexible group by charts with multiple series and formatters, no need for ChartView or TimeChartView.
- New, internal AppBuilder rebuild.

Improvements and Bug fixes on 0.9.0
-----------------------------------

- New, class name change 'BaseApp' to 'AppBuilder', import like: from flask.ext.appbuilder import AppBuilder
- New, can import expose decorator like: flask.ext.appbuilder import expose
- New, Changed 'Base' declarative name to 'Model' no need to add BaseMixin.
- New, No automatic dev's model creation, must invoke appbuilder.create_db()
- New, Change GeneralView to ModelView.
- Fix, Multiple database support correction.

Improvements and Bug fixes on 0.8.5
-----------------------------------

- New, security cleanup method, useful if you have changed a menu's name or view class name.
- Fix, internal security management optimization.
- New, security management method security_cleanup, will remove unused permissions, views and menus.
- Fix, removed automatic migration from version 0.3.
- New, adding views has classes without configuring the views db.session, session will
    be the same has the security tables.
- Fix, Security menu with wrong label and view association on 'Permission Views/Menu'.

Improvements and Bug fixes on 0.8.4
-----------------------------------

- Fix, js for remembering latest accordion was working like toggle (bs bug?).

Improvements and Bug fixes on 0.8.3
-----------------------------------

- Portuguese Brazil translations

Improvements and Bug fixes on 0.8.2
-----------------------------------

- Fix, possible to register on the menu different links to the same view class.
- Fix, init of baseapp missing init of baseviews list.

Improvements and Bug fixes on 0.8.1
-----------------------------------

- New, Python 3 partial support (babel will not work, caused by the babel package itself).
- Fix, Removed Flask-wtf requirement version limitation.
- New, test suite with nose.

Improvements and Bug fixes on 0.8.0
-----------------------------------

- New, Language, Simplified Chinese support.
- New, Language, Russian support.
- New, Language, German support.
- Fix, various translations.
- Fix,New support for virtual directory no need to install on root url, relative urls fixes.

Improvements and Bug fixes on 0.7.8
-----------------------------------

- New, login form style.
- Fix, Auto creation of user's models from Base.
- Fix, Removed double flash message on reset password form.
- New, support for icons on menu categories.
- New, remove "-" bettwen icons and menu labels.
- New, added optional parameter "label" and "category_label" for menu items. better security and i18n.

Improvements and Bug fixes on 0.7.7
-----------------------------------

- Fix, removed unnecessary log output.

Improvements and Bug fixes on 0.7.6
-----------------------------------

- Fix, TimeChartView not ordering dates correctly.

Improvements and Bug fixes on 0.7.5
-----------------------------------

- New, charts can be included has related views, can use it has tab, collapse and master-detail templates.
- Fix, login ldap, double message login failed correction.
- Fix, search responsive correction.
- New, accordion related view will record last choice on cookie.
- New, footer page, this can be overridden.

Improvements and Bug fixes on 0.7.4
-----------------------------------

- New, internal change, list functional header on lib.
- Fix, removed audit columns from user info view. Only shown on security admin.

Improvements and Bug fixes on 0.7.3
-----------------------------------

- Fix, removed forced cast to int on json conversion for DirectChartView. Better support for float.
- New, List for simple master detail, master works like a menu on the left side.
- Fix, fixed buttons size for show, edit, delete on lists. Buttons will not adapt to vertical.
- Fix, if no permissions for show, edit, delete, no empty cell is shown <th> or <td>.
- New, internal change, crud buttons on lib.

Improvements and Bug fixes on 0.7.2
-----------------------------------

- Fix, reported issue #15. Order by causes error on postgresql.

Improvements and Bug fixes on 0.7.1
-----------------------------------

- New, DirectChart support for xcol datetime.date type (Date or DateTime Model type).
- Fix, base_order property for DirectChartView.

Improvements and Bug fixes on 0.7.0
-----------------------------------

- New, ListBlock with pagination.
- New, Menu separator raises exception if it does not have a correct category.
- New, ShowBlockWidget different show detail presentation.
- Fix, login failed was not displaying error message.
- New, password is saved hashed on database.
- New, better database exceptions on security module
- New, User model columns: last_login, login_count, fail_login_count.
- New, User model column AuditMixin columns (created_on, changed_on, created_by_fk, changed_by_fk).
- New, AuditMixin allows null on FK columns.
- Fix, Add user on non sqlite db, failed if no email provided. Unique db constraint.
- Fix, form convert field exception handling (for method fields).
- New, support for "one to one" relations and "one to many", on forms, and filters (beta).
- Fix, ChartView unicode correction.
- New, DirectChartView to present database queries on numeric columns with multiple series.
- Fix, Adds all missing permissions to the role admin. Allways
- Fix, Removed User.active from possible search.
- New, unicode review for future python 3 support.

Improvements and Bug fixes on 0.6.14
------------------------------------

- Fix, url on time chart views to allow search on every group by column.
- New, support for float database type.

Improvements and Bug fixes on 0.6.13
------------------------------------

- BaseChartView *group_by_columns* empty list validation.
- Fix, url's for charts were changed to allow search on every group by column.

Improvements and Bug fixes on 0.6.11, 0.6.12
--------------------------------------------

- New, *get_file_orginal_name* helper function to remove UUID from file name.
- Fix, bug on related views was not adding new models. Impossible to insert on related views.

Improvements and Bug fixes on 0.6.10
------------------------------------

- Fix, Chart month bug, typo on code.

Improvements and Bug fixes on 0.6.9
-----------------------------------

- Fix, template table display not showing top first line.
- Fix, search widget permits dropdowns with overflow.
- Fix, removed style tag on init.html.
- New, ab.css for F.A.B custom styles.
- New, search widget with dropdown list of column choices, instead of buttons.

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

