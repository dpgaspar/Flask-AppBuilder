from flask import render_template, flash, redirect, url_for, request, send_file
from .filemanager import uuid_originalname
from .security.decorators import has_access
from .widgets import FormWidget, ListAddWidget
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

        widgets = self._list()
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

        widgets = self._show(pk)        
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

        widget = self._add()
        if not widget:
            return redirect(self._get_redirect())
        else:
            return render_template(self.add_template,
                                   title = self.add_title,
                                   widgets = widget,
                                   baseapp = self.baseapp)    

    """
    ---------------------------
            EDIT
    ---------------------------
    """
    @expose('/edit/<pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk):
        widgets = self._edit(pk)
        if not widgets:
            return redirect(self._get_redirect())
        else:
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
        self._delete(pk)
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
        
    
class ListAddViewMixin(BaseCRUDView):
    """
        Mix with general view to implement a list with add
    """
    list_widget = ListAddWidget
    
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
                                                add_widget = self._curr_form_widget,
                                                generalview_name = self.__class__.__name__
                                                )
        return widgets

    @expose('/list/', methods=['GET', 'POST'])
    @has_access
    def list(self):

        list_widgets = self._list()
        self._curr_form_widget = self._add()
        if not self._curr_form_widget:
            return redirect(self._get_redirect())
        return render_template(self.list_template,
                                        title = self.list_title,
                                        widgets = list_widgets,
                                        baseapp = self.baseapp)
