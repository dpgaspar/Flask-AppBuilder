Diagrams
========
========

This page will show various diagrams about the framework structure.

Class View Diagram Tree
-----------------------
-----------------------

All class views tree reflect functionality each layer is responsible for a certain goal. You will be essentially using
BaseViews, IndexViews and the leafs ModelView, chart views and form views.

.. blockdiag::

    blockdiag admin {

      BaseView;
      BaseView -> UtilView;
      BaseView -> IndexView;
      BaseView -> BaseFormView;
      BaseView -> MultipleView;
      BaseFormView -> SimpleFormView;
      BaseFormView -> PublicFormView;
      BaseView -> BaseModelView;
      BaseModelView -> BaseChartView;
      BaseModelView -> BaseCRUDView;
      BaseChartView -> GroupByChartView;
      BaseChartView -> DirectByChartView;
      BaseCRUDView -> RestCRUDView -> ModelView;
      BaseCRUDView -> MasterDetailView;
      BaseCRUDView -> CompactCRUDMixin;
    }


Next is a summary explanation for each class:

:BaseView: Collects all the exposed methods, creates the Flask blueprint and registers the URLs, initializes base permissions.
:UtilView: Implements exposes **back** for special back UI functionality.
:IndexView: Special view for rendering the index page.
:SimpleFormView: Subclass it to render WTForms.
:PublicFormView: Same as SimpleFormView but with public access only.
:BaseModelView: Class responsible for an initial datamodel layer, implements search form and filters.
:BaseChartView: Basic chart view functionality.
:GroupByChartView: Subclass it to render Google charts with group by queries.
:DirectByChartView: Subclass it to render Google charts with queries.
:BaseCRUDView: Implement base functionality for add, edit, delete, creates all forms.
:RestCRUDView: Exposes the JSON REST API for CRUD methods and more.
:ModelView: Subclass it to render your views based on models, with complete CRUD UI functionality.
:MasterDetailView: Renders a master ModelView and multiple detail ModelViews thar are database related.
:MultipleView: Renders multiple views on the same page (ex: ModelView and GroupByChartView)

Class Data Diagram Tree
-----------------------
-----------------------

All classes for data access aim for abstracting the backend.

.. blockdiag::

    blockdiag admin {

      BaseInterface;
      BaseInterface -> SQLAInterface;
      BaseInterface -> MongoEngineInterface;
      BaseInterface -> GenericInterface;
    }

:BaseInterface: Interface class, imposes a unique API layer for data access.
:SQLAInterface: Data access for SQLAlchemy.
:MongoEngineInterface: Data access for MongoEngine (MongoDB).
:GenericInterface: Data access for custom data structures.

Class Security Diagram Tree
---------------------------
---------------------------

Classes that are involved in implementing security. Register security views, implement various methods of authentication
manage permissions (insert/remove all permission on the backend).

.. blockdiag::

    blockdiag admin {

      BaseManager;
      BaseManager -> AbstractSecurityManager;
      AbstractSecurityManager -> BaseSecurityManager;
      BaseSecurityManager -> sqla.SecurityManager;
      BaseSecurityManager -> mongoengine.SecurityManager;
    }

:BaseManager: Base class for all Manager classes, holds AppBuilder class.
:AbstractSecurityManager: Abstract class for Security managers, defines the must have methods.
:BaseSecurityManager: Base class for security, registers security views, implements authentication,
 inserts/removes all permission on the database, manages roles/users and views.
:sqla.SecurityManager: Implements BaseSecurityManager for SQAlchemy.
:mongoengine.SecurityManager: Implements BaseSecurityManager for MongoEngine.

Security Models ERD
-------------------
-------------------

This is the ERD of the frameworks security models.

.. blockdiag::

    blockdiag admin {
      default_shape = roundedbox

      User;
      Role;
      Permission;
      ViewMenu;
      PermissionView;

      User <-> Role <-> PermissionView;
      PermissionView <- Permission;
      PermissionView <- ViewMenu;
    }

