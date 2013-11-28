Views
=====

BaseView
--------

All views derive from this class. it's constructor will register your exposed urls on flask as a Blueprint.

Generally you will not implement your views deriving from this class, unless your implementing a new base appbuilder view.

This class does not expose any url's, but provides a common base for all views.

Most importante Base Properties:

:route_base: The root base of your view
:template_folder: The base template folder
:base_permissions: The forced base permissions for your views, if not provided it will infer the permissions from the exposed methods and actions
    
SimpleFormView
--------------

Derive from this view to provide some base processing for your costumized form views.

Notice that this class derives from *BaseView* so all properties from the parent class can be overrided also.

Implement *form_get* and *form_post* to implement your form pre-processing and post-processing

Most importante Base Properties:

:form_title: The title to be presented (this is mandatory)
:form_columns: The form column names to include
:form: Your form class (WTFORM) (this is mandatory) 
    
GeneralView
-----------

This is the most important view. If you want to automatically implement create, edit, delete, show, and search
form your database tables, derive your views from this class.

Notice that this class derives from *BaseView* so all properties from the parent class can be overrided also.

Most importante Base Properties:

    - datamodel: SQLAModel (flask.ext.appbuilder.models.datamodel), take a look at quick start. (this is mandatory)

    - Titles
    :list_title: Title for list view 
    :show_title: Title for show view
    :add_title: Title for add view
    :edit_title: Title for edit view

    - Include Columns: lists of column names for the views 
    :list_columns: The columns to show on list (this is mandatory)
    :show_columns: The columns to show on show view
    :add_columns: The columns to show on add form, and also what will be added
    :edit_columns: The columns to show on edit form, and also what will be edited
    :order_columns: The columns allowed to order on lists
    :search_columns: The search form to filter the list

    - Properties for Labels and descriptions
        - label_columns: The labels to be shown for columns {'<COL NAME>': '<COL LABEL>', ....}
        - description_columns: The description to be shown for columns {'<COL NAME>': '<COL DESCRIPTION>', ....}

    - Optional Field set's, inspired on DJANGO field sets: fieldsets [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....]
        - show_fieldsets = []
        - add_fieldsets = []
        - edit_fieldsets = []

    - Properties for overriding auto form creation with your own defined forms (WTFORM)
        - add_form: Override this to override the add form auto creation
        - edit_form: Override this to override the edit form auto creation
        - search_form: : Override this to override the search form auto creation

    - validators_columns: Override this to implement your special validations for form columns
                        {'<COL NAME>': <WTForm Validator> }

    
    - Templates: override these to implement your own templates 
        - list_template = 'appbuilder/general/model/list.html'
        - edit_template = 'appbuilder/general/model/edit.html'
        - add_template = 'appbuilder/general/model/add.html'
        - show_template = 'appbuilder/general/model/show.html'

    - Widgets: override these to change the default display for the views implemented on this class. AppBuilder has some variations on these.
        - list_widget = ListWidget
        - edit_widget = FormWidget
        - add_widget = FormWidget
        - show_widget = ShowWidget
        - search_widget = SearchWidget


ChartView
---------

This a newly implemented, and provides a simple (and hopefully nice) way to draw some charts for your application.

This will show Google Charts based on group by of your tables.

Most importante Base Properties:

    - chart_title: Your Chart Title
    - chart_type: 'PieChart' or 'ColumnChart'
    - chart_3d: 'true' or 'false'
    - height: The height for you chart default is: '400px'
    - label_columns: : The labels to be shown for columns {'<COL NAME>': '<COL LABEL>', ....} (this is mandatory)
    - group_by_columns: A list for your possible group by's for your table (select * from <TABLE> group by [...])
    - datamodel: SQLAModel (flask.ext.appbuilder.models.datamodel), take a look at quick start. (this is mandatory)

Widgets
-------

