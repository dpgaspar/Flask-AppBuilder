import re
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file
from flask.ext.login import login_required
from flask.ext.babel import gettext, ngettext, lazy_gettext
from forms import GeneralModelConverter
from .security.decorators import has_access
from .filemanager import uuid_originalname
from .widgets import FormWidget, ShowWidget, ListWidget, SearchWidget



def expose(url='/', methods=('GET',)):
    """
        Use this decorator to expose views in your view classes.
    """
    def wrap(f):
        if not hasattr(f, '_urls'):
            f._urls = []
        f._urls.append((url, methods))
        return f
    return wrap
    
    
class BaseView(object):
    """
    Base View for all Views
    includes permission, app info
    """

    baseapp = None
    blueprint = None
    endpoint = None
    
    route_base = None
    template_folder = 'templates'
    static_folder='static'
    
    base_permissions = []
    redirect_url = '/'

    actions = []

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
            Create Flask blueprint.
        """
        # Store BaseApp instance
        self.baseapp = baseapp

        # If endpoint name is not provided, get it from the class name
        if not self.endpoint:
            self.endpoint = self.__class__.__name__.lower()

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

        self.register_urls()
        return self.blueprint

    def register_urls(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)

            if hasattr(attr, '_urls'):
                for url, methods in attr._urls:
                    self.blueprint.add_url_rule(url,
                                        attr_name,
                                        attr,
                                        methods=methods)
        

    def _prettify_name(self, name):
        return re.sub(r'(?<=.)([A-Z])', r' \1', name)


    def _get_redirect(self):
        if (request.args.get('next')):
            return request.args.get('next')
        else:
            return self.redirect_url

    def _get_group_by_args(self):
        group_by = request.args.get('group_by')
        if not group_by: group_by = ''
        return group_by

    def _get_order_args(self):
        order_column = request.args.get('order_column')
        order_direction = request.args.get('order_direction')
        if not order_column: order_column = ''
        if not order_direction: order_direction = ''
        return order_column, order_direction

    def _get_filter_args(self, filters={}):
        for n in request.args:
            re_match = re.findall('_flt_(.*)', n)
            if re_match:
                filters[re_match[0]] = request.args.get(n)
        return filters


    def _get_dict_from_form(self, form, filters={}):
        for item in form:
            if item.data:
                filters[item.name] = item.data
        return filters



class IndexView(BaseView):
    """
    Index View
    A simple view that implements the index for the site
    """

    route_base = ''

    index_template = 'appbuilder/index.html'

    @expose('/')
    @expose('/index/')
    def index(self):
        return render_template(self.index_template, baseapp = self.baseapp)

"""
----------------------------------
     SIMPLE FORM VIEW
----------------------------------
"""
class SimpleFormView(BaseView):
    """
    Simple Form View
    Basic functions used on forms:
    override form_get and form_post
    """

    form_template = 'appbuilder/general/model/edit.html'
    """ Widgets """
    edit_widget = FormWidget

    form_title = 'Form Title'
    form_columns = []
    form = None
    redirect_url = '/'

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
        pass

    def _get_edit_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['edit'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
                                                exclude_cols = exclude_cols,
                                                )
        return widgets



class BaseCRUDView(BaseView):
    route_base = '/general'
    datamodel = None
    related_views = []
    redirect_url = route_base + '/list'

    """ Titles """
    list_title = ""
    show_title = ""
    add_title = ""
    edit_title = ""

    """ Include Columns """
    list_columns = []
    show_columns = []
    add_columns = []
    edit_columns = []
    order_columns = []
    search_columns = []

    label_columns = {}
    description_columns = {}

    """ fieldsets [(<'TITLE'|None>, {'fields':[<F1>,<F2>,...]}),....] """
    show_fieldsets = []
    add_fieldsets = []
    edit_fieldsets = []

    """ Forms """
    add_form = None
    edit_form = None
    search_form = None

    validators_columns = {}

    """ Template Layouts """
    list_template = 'appbuilder/general/model/list.html'
    edit_template = 'appbuilder/general/model/edit.html'
    add_template = 'appbuilder/general/model/add.html'
    show_template = 'appbuilder/general/model/show.html'

    """ Widgets """
    list_widget = ListWidget
    edit_widget = FormWidget
    add_widget = FormWidget
    show_widget = ShowWidget
    search_widget = SearchWidget

    
    """ Additional Widgets """
    show_additional_links = []

    
    def _init_forms(self):
        
        conv = GeneralModelConverter(self.datamodel)        
        if not self.add_form:
            self.add_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    self.add_columns)
        if not self.edit_form:
            self.edit_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    self.edit_columns)        
        if not self.search_form:
            self.search_form = conv.create_form(self.label_columns,
                    self.description_columns,
                    self.validators_columns,
                    self.search_columns)


    def _init_vars(self):
        if self.show_fieldsets:
            self.show_columns = []
            for fieldset_item in self.show_fieldsets:                
                self.show_columns = self.show_columns + list(fieldset_item[1].get('fields'))                
        if self.add_fieldsets:
            self.add_columns = []
            for fieldset_item in self.add_fieldsets:
                self.add_columns = self.add_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.add_columns:
                self.add_columns = self.datamodel.get_columns_list()
        if self.edit_fieldsets:
            self.edit_columns = []
            for fieldset_item in self.edit_fieldsets:
                self.edit_columns = self.edit_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.edit_columns:
                self.edit_columns = self.datamodel.get_columns_list()
                        
        
    def __init__(self, **kwargs):
        self._init_vars()
        self._init_forms()
        super(BaseCRUDView, self).__init__(**kwargs)
    

    """
    --------------------------
            WIDGET METHODS
    --------------------------
    """
    def _get_related_list_widget(self, item, related_view, 
                                filters={}, order_column='', order_direction=''):

        fk = related_view.datamodel.get_related_fk(self.datamodel.obj)
        filters[fk] = item
        return related_view._get_list_widget(filters = filters, 
                    order_column = order_column, order_direction = order_direction)
        
    def _get_related_list_widgets(self, item, filters = {}, order_column='', order_direction='', 
                                widgets = {}, **args):
        widgets['related_lists'] = []
        for view in self.related_views:
            widgets['related_lists'].append(self._get_related_list_widget(item, view, filters, order_column, order_direction).get('list'))
        return widgets
    
    def _get_list_widget(self, filters={}, order_column='', order_direction='', widgets = {}, **args):

        lst = self.datamodel.query(filters, order_column, order_direction)
        pks = self.datamodel.get_keys(lst)
        widgets['list'] = self.list_widget(route_base = self.route_base,
                                                label_columns = self.label_columns,
                                                include_columns = self.list_columns,
                                                value_columns = self.datamodel.get_values(lst, self.list_columns),
                                                order_columns = self.order_columns,
                                                pks = pks,
                                                filters = filters,
                                                generalview_name = self.__class__.__name__
                                                )
        return widgets

    def _get_search_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['search'] = self.search_widget(route_base = self.route_base,
                                                form = form,
                                                exclude_cols = exclude_cols,
                                                )
        return widgets


    def _get_show_widget(self, id, widgets = {}, show_additional_links = []):
        if show_additional_links:
            additional_links = show_additional_links
        else: additional_links = self.show_additional_links
        print "ADDLINKS", additional_links
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
                                                exclude_cols = exclude_cols,
                                                fieldsets = self.add_fieldsets
                                                )
        return widgets

    def _get_edit_widget(self, form = None, exclude_cols = [], widgets = {}):
        widgets['edit'] = self.edit_widget(route_base = self.route_base,
                                                form = form,
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

    """
    -----------------------------------
     Methods to override
    -----------------------------------
    """
    @classmethod
    def pre_update(self, item):
        pass

    @classmethod
    def post_update(self, item):
        pass

    @classmethod
    def pre_add(self, item):
        pass

    @classmethod
    def post_add(self, item):
        pass

    @classmethod
    def pre_delete(self, item):
        pass

    @classmethod
    def post_delete(self, item):
        pass



class GeneralView(BaseCRUDView):
    """
    General View Class
    Responsible to handle all CRUD events
    List, Edit, Add, Show based on models
    """

    def __init__(self, **kwargs):
        super(GeneralView, self).__init__(**kwargs)

    """
    --------------------------------
            LIST
    --------------------------------
    """
    
    @expose('/list/', methods=['GET', 'POST'])
    @has_access
    def list(self):

        form = self.search_form.refresh()
        search_form = self.search_form(request.form)

        order_column, order_direction = self._get_order_args()

        filters = {}
        filters = self._get_filter_args(filters)
        filters = self._get_dict_from_form(search_form, filters)
        if (filters != {}):
            item = self.datamodel.obj()
            for filter_key in filters:
                try:
                    rel_obj = self.datamodel.get_related_obj(filter_key, filters.get(filter_key))
                    setattr(item, filter_key, rel_obj)
                    search_form = self.search_form(obj = item)
                    filters[filter_key] = rel_obj
                except:
                    setattr(item, filter_key, filters.get(filter_key))
                    search_form = self.search_form(obj = item)

        widgets = self._get_list_widget(filters, order_column, order_direction)
        widgets = self._get_search_widget(form = search_form, widgets = widgets)

        return render_template(self.list_template,
                                        title = self.list_title,
                                        widgets = widgets,
                                        baseapp = self.baseapp)



    """
    --------------------------------
            SHOW
    --------------------------------
    """
    @expose('/show/<int:id>', methods=['GET'])
    @has_access
    def show(self, id):

        widgets = self._get_show_widget(id)
        item = self.datamodel.get(id)
        widgets = self._get_related_list_widgets(item, filters = {}, order_column='', order_direction='', widgets = widgets)
        return render_template(self.show_template,
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
            return render_template(
                                                    self.add_template,
                                                    title = self.add_title,
                                                    widgets = widgets,
                                                    baseapp = self.baseapp
                                                    )    

    """
    ---------------------------
            EDIT
    ---------------------------
    """
    @expose('/edit/<int:pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk = 0):

        item = self.datamodel.get(pk)
        filters = self._get_filter_args(filters={})
        exclude_cols = self.datamodel.get_relation_filters(filters)

        if request.method == 'POST':
            form = self.edit_form(request.form)
            form = form.refresh(obj=item)
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
                widgets = self._get_related_list_widgets(item, filters = {}, order_column='', order_direction='', widgets = widgets)
                return render_template(self.edit_template,
                        title = self.edit_title,
                        widgets = widgets,
                        baseapp = self.baseapp,
                        related_views = self.related_views)
        else:
            form = self.edit_form(obj=item)
            form = form.refresh(obj=item)
            widgets = self._get_edit_widget(form = form, exclude_cols = exclude_cols)
            widgets = self._get_related_list_widgets(item, filters = {}, order_column='', order_direction='', widgets = widgets)
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
    @expose('/delete/<int:id>')
    @has_access
    def delete(self, id):
        item = self.datamodel.get(id)
        
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
