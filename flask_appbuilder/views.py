import re
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file
from flask.ext.login import login_required
from flask.ext.babel import gettext, ngettext, lazy_gettext
from forms import GeneralModelConverter
from .filemanager import uuid_originalname
from .security.decorators import has_access
from .widgets import FormWidget, ShowWidget, ListWidget, SearchWidget, ListCarousel
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
    
    base_permissions = []
    actions = []

    default_view = 'list'

    def __init__(self):
        """
            Initialization of base permissions
            based on exposed methods and actions
        """
        if not self.base_permissions:
            self.base_permissions = [
                ('can_' + attr_name)
                for attr_name in dir(self)
                if hasattr(getattr(self, attr_name),'_urls')
                ]
            for attr_name in dir(self):
                if hasattr(getattr(self, attr_name),'_action'):
                    action = ActionItem(*attr_name._action, func = getattr(self, attr_name))
                    self.base_permissions.append(action.name)
                    self.actions.append(action)

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
            

    def _get_group_by_args(self):
        group_by = request.args.get('group_by')
        if not group_by: group_by = ''
        return group_by

    def _get_page_args(self, pages = {}):
        """
            Get page arguments, return a dictionary
            { <VIEW_NAME>: PAGE_NUMBER }
        
            Arguments are passed: page_<VIEW_NAME>=<PAGE_NUMBER>
        
        """
        for arg in request.args:
            re_match = re.findall('page_(.*)', arg)
            if re_match:
                pages[re_match[0]] = int(request.args.get(arg))
        return pages



    def _get_order_args(self, orders = {}):
        """
            Get order arguments, return a dictionary
            { <VIEW_NAME>: (ORDER_COL, ORDER_DIRECTION) }
        
            Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'
        
        """
        for arg in request.args:
            re_match = re.findall('_oc_(.*)', arg)
            if re_match:
                orders[re_match[0]] = (request.args.get(arg),request.args.get('_od_' + re_match[0]))
        return orders
                

    def _get_filter_args(self, filters={}):
        for arg in request.args:
            re_match = re.findall('_flt_(.*)', arg)
            if re_match:
                # ignore select2 __None value
                if request.args.get(arg) not in ('__None',''):
                    filters[re_match[0]] = request.args.get(arg)
        return filters


    def _get_dict_from_form(self, form, filters={}):
        for item in form:
            if item.data:
                filters[item.name] = item.data
        return filters



class IndexView(BaseView):
    """
        A simple view that implements the index for the site
    """

    route_base = ''
    default_view = 'index'
    index_template = 'appbuilder/index.html'

    @expose('/')
    def index(self):
        return render_template(self.index_template, baseapp = self.baseapp)


class SimpleFormView(BaseView):
    """
        View for presenting your own forms
        Inherit from this view to provide some base processing for your costumized form views.

        Notice that this class inherits from BaseView so all properties from the parent class can be overrided also.

        Implement form_get and form_post to implement your form pre-processing and post-processing
    """

    form_template = 'appbuilder/general/model/edit.html'
    
    edit_widget = FormWidget
    form_title = 'Form Title'
    """ The form title to be displayed """
    form_columns = []
    """ The form columns to include """
    form = None
    """ The WTF form to render """
    
    @expose("/form", methods=['GET'])
    @has_access
    def this_form_get(self):
        form = self.form.refresh()
        self.form_get(form)
        widgets = self._get_edit_widget(form = form)
        return render_template(self.form_template,
            title = self.form_title,
            widgets = widgets,
            baseapp = self.baseapp
            )

    def form_get(self, form):
        """
        Override this method to implement your form processing
        """
        pass

    @expose("/form", methods=['POST'])
    @has_access
    def this_form_post(self):
        form = self.form.refresh()
        if form.validate_on_submit():
            self.form_post(form)
            return redirect(self._get_redirect())
        else:
            widgets = self._get_edit_widget(form = form)
            return render_template(
                    self.form_template,
                    title = self.form_title,
                    widgets = widgets,
                    baseapp = self.baseapp
                    )

    def form_post(self, form):
        """
        Override this method to implement your form processing
        """
        pass

    def _get_edit_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['edit'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
                                                exclude_cols = exclude_cols,
                                                )
        return widgets



class BaseCRUDView(BaseView):
    """
        The base class of GeneralView, all properties are inherited
        Customize GeneralView overriding this properties
    """
    
    
    datamodel = None
    """ Your sqla model you must initialize it like datamodel = SQLAModel(Permission, session) """
    related_views = []
    """ Views that will be displayed related with this one, must be instantiated """
    
    list_title = ""
    """ List Title """
    show_title = ""
    """ Show Title """
    add_title = ""
    """ Add Title """
    edit_title = ""
    """ Edit Title """

    
    list_columns = []
    """ Include Columns for lists view """
    show_columns = []
    """ Include Columns for show view """
    add_columns = []
    """ Include Columns for add view """
    edit_columns = []
    """ Include Columns for edit view """
    order_columns = []
    """ Allowed order columns """
    search_columns = []
    """ Allowed search columns """

    label_columns = {}
    description_columns = {}
    
    add_form_extra_fields = {}
    """ Add extra fields to the Add form using this property """
    edit_form_extra_fields = {}
    """ Add extra fields to the Edit form using this property """
    
    page_size = 30

    
    show_fieldsets = []
    """ show fieldsets [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....] """
    add_fieldsets = []
    """ add fieldsets [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....] """
    edit_fieldsets = []
    """ edit fieldsets [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....] """

    
    add_form = None
    """ To implement your own add WTF form for Add """
    edit_form = None
    """ To implement your own add WTF form for Edit """
    search_form = None
    """ To implement your own add WTF form for Search """

    validators_columns = {}

    
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
    """ Search widget override """
        
    show_additional_links = []

    
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
        if not self.search_form:
            self.search_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    [],
                    self.search_columns)

    def _init_titles(self):
        if not self.list_title:
            self.list_title = 'List ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.add_title:
            self.add_title = 'Add ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.edit_title:
            self.edit_title = 'Edit ' + self._prettify_name(self.datamodel.obj.__name__)
        if not self.show_title:
            self.show_title = 'Show ' + self._prettify_name(self.datamodel.obj.__name__)

    def _init_vars(self):
        self._init_titles()
            
        list_cols = self.datamodel.get_columns_list()
        for col in list_cols:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)
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
                        
        
    def __init__(self, **kwargs):
        self._init_vars()
        self._init_forms()
        super(BaseCRUDView, self).__init__(**kwargs)
    

    def _get_related_list_widget(self, item, related_view, 
                                filters={}, order_column='', order_direction='',
                                page=None, page_size=None):

        fk = related_view.datamodel.get_related_fk(self.datamodel.obj)
        filters[fk] = item
        return related_view._get_list_widget(filters = filters, 
                    order_column = order_column, order_direction = order_direction, page=page, page_size=page_size)
        
    def _get_related_list_widgets(self, item, filters = {}, orders = {}, 
                                pages=None, widgets = {}, **args):
        widgets['related_lists'] = []
        for view in self.related_views:
            if orders.get(view.__class__.__name__):
                order_column, order_direction = orders.get(view.__class__.__name__)
            else: order_column, order_direction = '',''
            widgets['related_lists'].append(self._get_related_list_widget(item, view, filters, 
                    order_column, order_direction, page=pages.get(view.__class__.__name__), page_size=view.page_size).get('list'))
        return widgets
    
    def _get_list_widget(self, filters = {}, 
                        order_column = '', 
                        order_direction = '',
                        page = None,
                        page_size = None,
                        widgets = {}, **args):

        count, lst = self.datamodel.query(filters, order_column, order_direction, page=page, page_size=page_size)
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
                                                filters = filters,
                                                generalview_name = self.__class__.__name__
                                                )
        return widgets

    def _get_search_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['search'] = self.search_widget(route_base = self.route_base,
                                                form = form,
                                                include_cols = self.search_columns,
                                                exclude_cols = exclude_cols,
                                                )
        return widgets


    def _get_show_widget(self, id, widgets = {}, show_additional_links = []):
        if show_additional_links:
            additional_links = show_additional_links
        else: additional_links = self.show_additional_links
        item = self.datamodel.get(id)
        widgets['show'] = self.show_widget(route_base = self.route_base,
                                                pk = id,
                                                label_columns = self.label_columns,
                                                include_columns = self.show_columns,
                                                value_columns = self.datamodel.get_values_item(item, self.show_columns),
                                                additional_links = additional_links,
                                                fieldsets = self.show_fieldsets
                                                )
        return widgets


    def _get_add_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['add'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
                                                include_cols = self.add_columns,
                                                exclude_cols = exclude_cols,
                                                fieldsets = self.add_fieldsets
                                                )
        return widgets

    def _get_edit_widget(self, form = None, exclude_cols = [], widgets = {}):
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


class GeneralView(BaseCRUDView):
    """
        This is the most important view. If you want to automatically implement create, edit, delete, show, and search form your database tables, inherit your views from this class.

        Notice that this class inherits from BaseView so all properties from the parent class can be overrided also.
    """

    def __init__(self, **kwargs):
        super(GeneralView, self).__init__(**kwargs)

    """
    --------------------------------
            LIST
    --------------------------------
    """
    
    @expose('/list/')
    @has_access
    def list(self):

        form = self.search_form.refresh()
        
        if self._get_order_args().get(self.__class__.__name__):
            order_column, order_direction = self._get_order_args().get(self.__class__.__name__)
        else: order_column, order_direction = '',''
        page = self._get_page_args().get(self.__class__.__name__)

        filters = {}
        filters = self._get_filter_args(filters)
        if (filters != {}):
            item = self.datamodel.obj()
            for filter_key in filters:
                # on related models translate id to model obj
                try:
                    rel_obj = self.datamodel.get_related_obj(filter_key, filters.get(filter_key))
                    setattr(item, filter_key, rel_obj)
                    form = self.search_form(obj = item)
                    filters[filter_key] = rel_obj
                except:
                    setattr(item, filter_key, filters.get(filter_key))
                    form = self.search_form(obj = item)

        widgets = self._get_list_widget(filters = filters, 
                    order_column = order_column, 
                    order_direction = order_direction, 
                    page = page, 
                    page_size = self.page_size)
        widgets = self._get_search_widget(form = form, widgets = widgets)

        return render_template(self.list_template,
                                        title = self.list_title,
                                        widgets = widgets,
                                        baseapp = self.baseapp)



    """
    --------------------------------
            SHOW
    --------------------------------
    """
    @expose('/show/<int:pk>', methods=['GET'])
    @has_access
    def show(self, pk):

        widgets = self._get_show_widget(pk)
        item = self.datamodel.get(pk)
        pages = self._get_page_args()
        orders = self._get_order_args()
        
        widgets = self._get_related_list_widgets(item, filters = {}, orders = orders, 
                pages = pages, widgets = widgets)
        return render_template(self.show_template,
                           pk = pk,
                           title = self.show_title,
                           widgets = widgets,
                           baseapp = self.baseapp,
                           related_views = self.related_views)



    """
    ---------------------------
            ADD
    ---------------------------
    """
    @expose('/add', methods=['GET', 'POST'])
    @has_access
    def add(self):

        filters = self._get_filter_args(filters={})

        form = self.add_form.refresh()
        exclude_cols = self.datamodel.get_relation_filters(filters)

        if form.validate_on_submit():
            item = self.datamodel.obj()
            form.populate_obj(item)
            for filter_key in exclude_cols:
                rel_obj = self.datamodel.get_related_obj(filter_key, filters.get(filter_key))
                setattr(item, filter_key, rel_obj)
                        
            self.pre_add(item)
            self.datamodel.add(item)
            self.post_add(item)
            return redirect(self._get_redirect())
        else:
            widgets = self._get_add_widget(form = form, exclude_cols = exclude_cols)
            return render_template(self.add_template,
                                   title = self.add_title,
                                   widgets = widgets,
                                   baseapp = self.baseapp)    

    """
    ---------------------------
            EDIT
    ---------------------------
    """
    @expose('/edit/<int:pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk = 0):

        pages = self._get_page_args()
        orders = self._get_order_args()
        
        item = self.datamodel.get(pk)
        filters = self._get_filter_args(filters={})
        exclude_cols = self.datamodel.get_relation_filters(filters)

        if request.method == 'POST':
            form = self.edit_form(request.form)
            form = form.refresh(obj=item)
            # trick to pass unique validation
            form._id = pk
            if form.validate():
                form.populate_obj(item)

                for filter_key in exclude_cols:
                    rel_obj = self.datamodel.get_related_obj(filter_key, filters.get(filter_key))
                    setattr(item, filter_key, rel_obj)
                
                self.pre_update(item)
                self.datamodel.edit(item)
                self.post_update(item)
                return redirect(self._get_redirect())
            else:
                widgets = self._get_edit_widget(form = form, exclude_cols = exclude_cols)
                widgets = self._get_related_list_widgets(item, filters = {}, 
                        orders = orders, pages = pages, widgets = widgets)
                return render_template(self.edit_template,
                        title = self.edit_title,
                        widgets = widgets,
                        baseapp = self.baseapp,
                        related_views = self.related_views)
        else:
            form = self.edit_form(obj=item)
            form = form.refresh(obj=item)
            widgets = self._get_edit_widget(form = form, exclude_cols = exclude_cols)
            widgets = self._get_related_list_widgets(item, filters = {}, 
                        orders = orders, pages = pages, widgets = widgets)                
            return render_template(self.edit_template,
                            title = self.edit_title,
                            widgets = widgets,
                            baseapp = self.baseapp,
                            related_views = self.related_views)


    """
    ---------------------------
            DELETE
    ---------------------------
    """
    @expose('/delete/<int:pk>')
    @has_access
    def delete(self, pk):
        item = self.datamodel.get(pk)
        
        self.pre_delete(item)
        self.datamodel.delete(item)
        self.post_delete(item)        
        return redirect(self._get_redirect())


    @expose('/download/<string:filename>')
    @has_access
    def download(self, filename):
        return send_file(self.baseapp.app.config['UPLOAD_FOLDER'] + filename, 
                    attachment_filename = uuid_originalname(filename), 
                    as_attachment = True)
        



class AdditionalLinkItem():
    name = ""
    label = ""
    href = ""
    icon = ""

    def __init__(self, name, label, href, icon=""):
        self.name = name
        self.label = label
        self.href = href
        self.icon = icon
