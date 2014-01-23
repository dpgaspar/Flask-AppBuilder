import re
from flask import Blueprint
from flask.ext.babelpkg import gettext, ngettext, lazy_gettext
from forms import GeneralModelConverter
from .widgets import FormWidget, ShowWidget, ListWidget, SearchWidget, ListCarousel
from .models.filters import Filters, FilterRelationOneToManyEqual
from .actions import ActionItem

def expose(url='/', methods=('GET',)):
    """
        Use this decorator to expose views in your view classes.
       
        :param url:
            Relative URL for the view
        :param methods:
            Allowed HTTP methods. By default only GET is allowed.
    """
    def wrap(f):
        if not hasattr(f, '_urls'):
            f._urls = []
        f._urls.append((url, methods))
        return f
    return wrap


class BaseView(object):
    """
        All views inherit from this class. it's constructor will register your exposed urls on flask as a Blueprint.

        This class does not expose any urls, but provides a common base for all views.
        
        Extend this class if you want to expose methods for your own templates        
    """

    baseapp = None
    blueprint = None
    endpoint = None
    
    route_base = None
    """ Override this if you want to define your own relative url """
    
    template_folder = 'templates'
    static_folder='static'
    base_permissions = None    
    default_view = 'list'

    def __init__(self):
        """
            Initialization of base permissions
            based on exposed methods and actions
        """
        if self.base_permissions is None:
            self.base_permissions = [
                ('can_' + attr_name)
                for attr_name in dir(self)
                if hasattr(getattr(self, attr_name),'_urls')
                ]


    def create_blueprint(self, baseapp, 
                        endpoint = None, 
                        static_folder = None):
        """
            Create Flask blueprint. You will generally not use it
            
            :param baseapp:
               the BaseApp application
            :param endpoint:
               endpoint override for this blueprint, will assume class name if not provided
            :param static_folder:
               the relative override for static folder, if ommited application will use the baseapp static
        """
        # Store BaseApp instance
        self.baseapp = baseapp

        # If endpoint name is not provided, get it from the class name
        if not self.endpoint:
            self.endpoint = self.__class__.__name__

        if self.route_base is None:
            self.route_base = '/' + self.__class__.__name__.lower()

        self.static_folder = static_folder
        if not static_folder:
        # Create blueprint and register rules
            self.blueprint = Blueprint(self.endpoint, __name__,
                                   url_prefix=self.route_base,
                                   template_folder=self.template_folder)
        else:
            self.blueprint = Blueprint(self.endpoint, __name__,
                                   url_prefix=self.route_base,
                                   template_folder=self.template_folder,
                                   static_folder = static_folder)

        self._register_urls()
        return self.blueprint

    def _register_urls(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)

            if hasattr(attr, '_urls'):
                for url, methods in attr._urls:
                    self.blueprint.add_url_rule(url,
                                        attr_name,
                                        attr,
                                        methods=methods)
    
    
    def render_template(self, template, **kwargs):
        kwargs['_'] = babel.gettext
        return render_template(template, **kwargs)

    def _prettify_name(self, name):
        """
            Prettify pythonic variable name.

            For example, 'hello_world' will be converted to 'Hello World'

            :param name:
                Name to prettify.
        """
        return re.sub(r'(?<=.)([A-Z])', r' \1', name)

    def _prettify_column(self, name):
        """
            Prettify pythonic variable name.

            For example, 'hello_world' will be converted to 'Hello World'

            :param name:
                Name to prettify.
        """
        return name.replace('_', ' ').title()


    def _get_redirect(self):
        if (request.args.get('next')):
            return request.args.get('next')
        else:
            try:
                return url_for('%s.%s' % (self.endpoint, self.default_view))
            except:
                return url_for('%s.%s' % (self.baseapp.indexview.endpoint, self.baseapp.indexview.default_view))
            

class BaseModelView(BaseView):
    """
        The base class of GeneralView and ChartView, all properties are inherited
        Customize GeneralView and ChartView overriding this properties
    """

    datamodel = None
    """ 
        Your sqla model you must initialize it like::
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)
    """
    search_columns = None
    """ 
        List with allowed search columns, if not provided all possible search columns will be used 
        If you want to limit the search (*filter*) columns possibilities, define it with a list of column names from your model::
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)
                search_columns = ['name','address']
             
    """
    label_columns = None
    """ 
        Dictionary of labels for your columns, override this if you want diferent pretify labels 
        
        example (will just override the label for name column)::
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)
                label_columns = {'name':'My Name Label Override'}
        
    """    
    search_form = None
    """ To implement your own add WTF form for Search """
    base_filters = None
    """ 
        Filter the view use: ['column_name',BaseFilter,'value'] 
    
        example::
        
            def get_user():
                return g.user
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)
                base_filters = [['created_by', FilterEqualFunction, get_user],
                                ['name', FilterStartsWith, 'a']]
                                            
    """
    _base_filters = None
    """ Internal base Filter from class Filters will always filter view """
    _filters = None
    """ Filters object will calculate all possible filter types based on search_columns """

    def __init__(self, **kwargs):
        """
            Constructor
        """
        self._base_model_init_vars()
        self._base_model_init_forms()
        self._filters = Filters(self.search_columns, self.datamodel)
        super(BaseModelView, self).__init__(**kwargs)
        

    def _base_model_init_vars(self):
        self.label_columns = self.label_columns or {}
        self.base_filters = self.base_filters or []
        self._base_filters = Filters().add_filter_list(self.datamodel, self.base_filters)
        list_cols = self.datamodel.get_columns_list()
        self.search_columns = self.search_columns or list_cols
        for col in list_cols:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)
        
    def _base_model_init_forms(self):
        conv = GeneralModelConverter(self.datamodel)
        if not self.search_form:
            self.search_form = conv.create_form(self.label_columns,
                    {}, {}, [], self.search_columns)


    def _get_search_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['search'] = self.search_widget(route_base = self.route_base,
                                                form = form,
                                                include_cols = self.search_columns,
                                                exclude_cols = exclude_cols,
                                                filters = self._filters
                                                )
        return widgets



class BaseCRUDView(BaseModelView):
    """
        The base class for GeneralView, all properties are inherited
        Customize GeneralView overriding this properties
    """
    
    related_views = None
    """ 
        List with instantiated GeneralView classes
        That will be displayed related with this one using relationship sqlalchemy property
    """
    list_title = ""
    """ List Title, if not configured the default is 'List ' with pretty model name """
    show_title = ""
    """ Show Title , if not configured the default is 'Show ' with pretty model name """
    add_title = ""
    """ Add Title , if not configured the default is 'Add ' with pretty model name """
    edit_title = ""
    """ Edit Title , if not configured the default is 'Edit ' with pretty model name """

    list_columns = None
    """ Include Columns for lists view """
    show_columns = None
    """ Include Columns for show view """
    add_columns = None
    """ Include Columns for add view """
    edit_columns = None
    """ Include Columns for edit view """
    order_columns = None
    """ Allowed order columns """
    
    page_size = 10
    """ 
        Use this property to change default page size 
    """
    base_order = None
    """ 
        Use this property to set default ordering for lists ('col_name','asc|desc')::
    
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)
                base_order = ('my_column_name','asc')
        
    """
    
    show_fieldsets = None
    """ 
        show fieldsets django style [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....]
        
        ::
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)

                show_fieldsets = [
                    ('Summary',{'fields':['name','address','group']}),
                    ('Personal Info',{'fields':['birthday','personal_phone'],'expanded':False}),
                    ]

    """
    add_fieldsets = None
    """ 
        add fieldsets django style (look at show_fieldsets for an example)
    """
    edit_fieldsets = None
    """ 
        edit fieldsets django style (look at show_fieldsets for an example)
    """
    
    description_columns = None
    """ 
        Dictionary with column descriptions that will be shown on the forms::
        
            class MyView(GeneralView):
                datamodel = SQLAModel(MyTable, db.session)

                description_columns = {'name','your models name column','address','the address column'}
    """
    validators_columns = None
    """ Dictionary to add your own validators for forms """
    add_form_extra_fields = None
    """ Dictionary to add extra fields to the Add form using this property """
    edit_form_extra_fields = None
    """ Dictionary to Add extra fields to the Edit form using this property """
    
    
    add_form = None
    """ To implement your own add WTF form for Add """
    edit_form = None
    """ To implement your own add WTF form for Edit """
    
    
    list_template = 'appbuilder/general/model/list.html'
    """ Your own add jinja2 template for list """
    edit_template = 'appbuilder/general/model/edit.html'
    """ Your own add jinja2 template for edit """
    add_template = 'appbuilder/general/model/add.html'
    """ Your own add jinja2 template for add """
    show_template = 'appbuilder/general/model/show.html'
    """ Your own add jinja2 template for show """

    list_widget = ListWidget
    """ List widget override """
    edit_widget = FormWidget
    """ Edit widget override """
    add_widget = FormWidget
    """ Add widget override """
    show_widget = ShowWidget
    """ Show widget override """
    search_widget = SearchWidget
    """ Search widget you can override with your own """
        
    actions = None

    def __init__(self, **kwargs):
        super(BaseCRUDView, self).__init__(**kwargs)
        self._init_properties()
        self._init_forms()
        self._init_titles()

        self.actions = {}
        for attr_name in dir(self):
            func = getattr(self, attr_name)
            if hasattr(func,'_action'):
                action = ActionItem(*func._action, func = func)
                self.base_permissions.append(action.name)
                self.actions[action.name] = (action)


    def _init_forms(self):
        conv = GeneralModelConverter(self.datamodel)        
        if not self.add_form:
            self.add_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    self.add_form_extra_fields,
                    self.add_columns)
        if not self.edit_form:
            self.edit_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    self.edit_form_extra_fields,
                    self.edit_columns)
        

    def _init_titles(self):
        if not self.list_title:
            self.list_title = 'List ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.add_title:
            self.add_title = 'Add ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.edit_title:
            self.edit_title = 'Edit ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.show_title:
            self.show_title = 'Show ' + self._prettify_name(self.datamodel.obj.__name__)

    def _init_properties(self):
        self.related_views = self.related_views or []
        self.description_columns = self.description_columns or {}
        self.validators_columns = self.validators_columns or {}
        self.add_form_extra_fields = self.add_form_extra_fields or {}
        self.edit_form_extra_fields = self.edit_form_extra_fields or {}
        order_cols = self.datamodel.get_order_columns_list()
        list_cols = self.datamodel.get_columns_list()
        self.list_columns = self.list_columns or [order_cols[0]]
        self.order_columns = self.order_columns or order_cols
        if self.show_fieldsets:
            self.show_columns = []
            for fieldset_item in self.show_fieldsets:                
                self.show_columns = self.show_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.show_columns:
                self.show_columns = list_cols
        if self.add_fieldsets:
            self.add_columns = []
            for fieldset_item in self.add_fieldsets:
                self.add_columns = self.add_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.add_columns:
                self.add_columns = list_cols
        if self.edit_fieldsets:
            self.edit_columns = []
            for fieldset_item in self.edit_fieldsets:
                self.edit_columns = self.edit_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.edit_columns:
                self.edit_columns = list_cols
        

    def _get_related_list_widget(self, item, related_view, 
                                order_column='', order_direction='',
                                page=None, page_size=None):

        fk = related_view.datamodel.get_related_fk(self.datamodel.obj)
        filters = Filters().add_filter(fk, FilterRelationOneToManyEqual, 
                related_view.datamodel, self.datamodel.get_pk_value(item))
        return related_view._get_list_widget(filters = filters,
                    order_column = order_column,
                    order_direction = order_direction,
                    page=page, page_size=page_size)

    def _get_related_list_widgets(self, item, orders = {}, pages=None, page_sizes=None, widgets = {}, **args):
        widgets['related_lists'] = []
        for view in self.related_views:
            if orders.get(view.__class__.__name__):
                order_column, order_direction = orders.get(view.__class__.__name__)
            else: order_column, order_direction = '',''
            widgets['related_lists'].append(self._get_related_list_widget(item, view, 
                    order_column, order_direction, 
                    page=pages.get(view.__class__.__name__), page_size=page_sizes.get(view.__class__.__name__)).get('list'))
        return widgets
    
    def _get_list_widget(self, filters,
                        actions = None,
                        order_column = '', 
                        order_direction = '',
                        page = None,
                        page_size = None,
                        widgets = {}, **args):

        """ get joined base filter and current active filter for query """
        actions = actions or self.actions
        page_size = page_size or self.page_size
        if not order_column and self.base_order:
            order_column, order_direction = self.base_order    
        joined_filters = filters.get_joined_filters(self._base_filters)
        count, lst = self.datamodel.query(joined_filters, order_column, order_direction, page=page, page_size=page_size)
        pks = self.datamodel.get_keys(lst)
        widgets['list'] = self.list_widget(route_base = self.route_base,
                                                label_columns = self.label_columns,
                                                include_columns = self.list_columns,
                                                value_columns = self.datamodel.get_values(lst, self.list_columns),
                                                order_columns = self.order_columns,
                                                page = page,
                                                page_size = page_size,
                                                count = count,
                                                pks = pks,
                                                actions = actions,
                                                filters = filters,
                                                generalview_name = self.__class__.__name__
                                                )
        return widgets


    def _get_show_widget(self, id, widgets = None, actions = None):
        widgets = widgets or {}
        actions = actions or self.actions
        item = self.datamodel.get(id)
        widgets['show'] = self.show_widget(route_base = self.route_base,
                                                pk = id,
                                                label_columns = self.label_columns,
                                                include_columns = self.show_columns,
                                                value_columns = self.datamodel.get_values_item(item, self.show_columns),
                                                actions = actions,
                                                fieldsets = self.show_fieldsets,
                                                generalview_name = self.__class__.__name__
                                                )
        return widgets


    def _get_add_widget(self, form = None, exclude_cols = None, widgets = None):
        exclude_cols = exclude_cols or []
        widgets = widgets or {}
        widgets['add'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
                                                include_cols = self.add_columns,
                                                exclude_cols = exclude_cols,
                                                fieldsets = self.add_fieldsets
                                                )
        return widgets

    def _get_edit_widget(self, form = None, exclude_cols = None, widgets = None):
        exclude_cols = exclude_cols or []
        widgets = widgets or {}
        widgets['edit'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
                                                include_cols = self.edit_columns,
                                                exclude_cols = exclude_cols,
                                                fieldsets = self.edit_fieldsets
                                                )
        return widgets


    def debug(self):

        print self.__class__.__name__, "SHOW FS", self.show_fieldsets
        print self.__class__.__name__, "SHOW COL", self.show_columns
        print self.__class__.__name__, "ADD FS", self.add_fieldsets
        print self.__class__.__name__, "ADD COL", self.add_columns
        print self.__class__.__name__, "EDIT FS", self.edit_fieldsets
        print self.__class__.__name__, "EDIT COL", self.edit_columns
        print self.__class__.__name__, "LIST COL", self.list_columns

    
    def pre_update(self, item):
        """
            Override this, will be called before update
        """
        pass

    def post_update(self, item):
        """
            Override this, will be called after update
        """        
        pass

    def pre_add(self, item):
        """
            Override this, will be called before add
        """        
        pass

    def post_add(self, item):
        """
            Override this, will be called after update
        """        
        pass

    def pre_delete(self, item):
        """
            Override this, will be called before delete
        """        
        pass

    def post_delete(self, item):
        """
            Override this, will be called after delete
        """        
        pass
