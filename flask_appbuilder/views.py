from flask import render_template, flash, redirect, url_for, request, send_file
from .filemanager import uuid_originalname
from urltools import *
from .security.decorators import has_access
from .widgets import FormWidget
from .actions import action
from .baseviews import expose, BaseView, BaseCRUDView


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
        Inherit from this view to provide some base processing for your customized form views.

        Notice that this class inherits from BaseView so all properties from the parent class can be overridden also.

        Implement form_get and form_post to implement your form pre-processing and post-processing
    """

    form_template = 'appbuilder/general/model/edit.html'
    
    edit_widget = FormWidget
    form_title = ''
    """ The form title to be displayed """
    form_columns = None
    """ The form columns to include, if empty will include all"""
    form = None
    """ The WTF form to render """
    form_fieldsets = None
    
    def _init_vars(self):
        self.form_columns = self.form_columns or []
        self.form_fieldsets = self.form_fieldsets or []
        list_cols = [field.name for field in self.form.refresh()]
        if self.form_fieldsets:
            self.form_columns = []
            for fieldset_item in self.form_fieldsets:
                self.form_columns = self.form_columns + list(fieldset_item[1].get('fields'))
        else:
            if not self.form_columns:
                self.form_columns = list_cols
        
    
    @expose("/form", methods=['GET'])
    @has_access
    def this_form_get(self):
        self._init_vars()
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
        self._init_vars()
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
                                                include_cols = self.form_columns,
                                                exclude_cols = exclude_cols,
                                                fieldsets = self.form_fieldsets
                                                )         
        return widgets



class GeneralView(BaseCRUDView):
    """
        This is the CRUD generic view. If you want to automatically implement create, edit, delete, show, and list from your database tables, inherit your views from this class.

        Notice that this class inherits from BaseCRUDView and BaseModelView so all properties from the parent class can be overriden.
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
        
        if get_order_args().get(self.__class__.__name__):
            order_column, order_direction = get_order_args().get(self.__class__.__name__)
        else: order_column, order_direction = '',''
        page = get_page_args().get(self.__class__.__name__)
        page_size = get_page_size_args().get(self.__class__.__name__)
        
        get_filter_args(self._filters)
        
        widgets = self._get_list_widget(filters = self._filters, 
                    order_column = order_column, 
                    order_direction = order_direction, 
                    page = page, 
                    page_size = page_size)
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
    @expose('/show/<pk>', methods=['GET'])
    @has_access
    def show(self, pk):

        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()

        widgets = self._get_show_widget(pk)
        item = self.datamodel.get(pk)
                
        widgets = self._get_related_list_widgets(item, orders = orders, 
                pages = pages, page_sizes = page_sizes, widgets = widgets)
        
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

        get_filter_args(self._filters)

        form = self.add_form.refresh()
        exclude_cols = self._filters.get_relation_cols()

        if form.validate_on_submit():
            item = self.datamodel.obj()
            form.populate_obj(item)
            for filter_key in exclude_cols:
                rel_obj = self.datamodel.get_related_obj(filter_key, self._filters.get_filter_value(filter_key))
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
    @expose('/edit/<pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk):

        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()
        
        item = self.datamodel.get(pk)
        # convert pk to correct type, if pk is non string type.
        pk = self.datamodel.get_pk_value(item)
        get_filter_args(self._filters)
        exclude_cols = self._filters.get_relation_cols()

        if request.method == 'POST':
            form = self.edit_form(request.form)
            form = form.refresh(obj=item)
            # trick to pass unique validation
            form._id = pk
            if form.validate():
                form.populate_obj(item)
                # fill the form with the suppressed cols, generated from exclude_cols
                for filter_key in exclude_cols:
                    rel_obj = self.datamodel.get_related_obj(filter_key, self._filters.get_filter_value(filter_key))
                    setattr(item, filter_key, rel_obj)
                
                self.pre_update(item)
                self.datamodel.edit(item)
                self.post_update(item)
                return redirect(self._get_redirect())
            else:
                widgets = self._get_edit_widget(form = form, exclude_cols = exclude_cols)
                widgets = self._get_related_list_widgets(item, filters = {}, 
                        orders = orders, pages = pages, page_sizes=page_sizes, widgets = widgets)
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
                        orders = orders, pages = pages, page_sizes=page_sizes, widgets = widgets)                
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
    @expose('/delete/<pk>')
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


    @expose('/action/<string:name>/<pk>')
    @has_access
    def action(self, name, pk):
        if self.baseapp.sm.has_access(name, self.__class__.__name__):
            action = self.actions.get(name)
            return action.func(self.datamodel.get(pk))
        else:
            flash("Access is Denied %s %s" % (name, self.__class__.__name__),"danger")
            return redirect('.')
        
