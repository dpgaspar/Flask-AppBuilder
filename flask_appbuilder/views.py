import logging
from flask import flash, redirect, send_file, jsonify, make_response
from ._compat import as_unicode
from flask_babelpkg import lazy_gettext
from .filemanager import uuid_originalname
from .widgets import FormWidget, GroupFormListWidget, ListMasterWidget
from .baseviews import BaseView, BaseCRUDView, expose
from .security.decorators import has_access, permission_name
from .urltools import *


log = logging.getLogger(__name__)


class IndexView(BaseView):
    """
        A simple view that implements the index for the site
    """
    route_base = ''
    default_view = 'index'
    index_template = 'appbuilder/index.html'

    @expose('/')
    def index(self):
        self.update_redirect()
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class UtilView(BaseView):
    """
        A simple view that implements special util routes.
        At the moment it only supports the back special endpoint.
    """
    route_base = ''
    default_view = 'back'

    @expose('/back')
    def back(self):
        return redirect(self.get_redirect())



class SimpleFormView(BaseView):
    """
        View for presenting your own forms
        Inherit from this view to provide some base processing for your customized form views.

        Notice that this class inherits from BaseView so all properties from the parent class can be overridden also.

        Implement form_get and form_post to implement your form pre-processing and post-processing
    """

    form_template = 'appbuilder/general/model/edit.html'

    edit_widget = FormWidget
    """ Form widget to override """
    form_title = ''
    """ The form title to be displayed """
    form_columns = None
    """ The form columns to include, if empty will include all"""
    form = None
    """ The WTF form to render """
    form_fieldsets = None
    """ Form field sets """
    default_view = 'this_form_get'
    """ The form view default entry endpoint """


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
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return self.render_template(self.form_template,
                               title=self.form_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder
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
            return redirect(self.get_redirect())
        else:
            widgets = self._get_edit_widget(form=form)
            return self.render_template(
                self.form_template,
                title=self.form_title,
                widgets=widgets,
                appbuilder=self.appbuilder
            )

    def form_post(self, form):
        """
            Override this method to implement your form processing
        """
        pass

    def _get_edit_widget(self, form=None, exclude_cols=None, widgets=None):
        exclude_cols = exclude_cols or []
        widgets = widgets or {}
        widgets['edit'] = self.edit_widget(route_base=self.route_base,
                                           form=form,
                                           include_cols=self.form_columns,
                                           exclude_cols=exclude_cols,
                                           fieldsets=self.form_fieldsets
        )
        return widgets


class PublicFormView(BaseView):
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
    """ The field sets for the form widget """
    default_view = 'this_form_get'
    """ The form view default entry endpoint """

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
    def this_form_get(self):
        self._init_vars()
        form = self.form.refresh()
        self.form_get(form)
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return self.render_template(self.form_template,
                               title=self.form_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder
        )

    def form_get(self, form):
        """
            Override this method to implement your form processing
        """
        pass

    @expose("/form", methods=['POST'])
    def this_form_post(self):
        self._init_vars()
        form = self.form.refresh()
        if form.validate_on_submit():
            self.form_post(form)
            return redirect(self.get_redirect())
        else:
            widgets = self._get_edit_widget(form=form)
            return self.render_template(
                self.form_template,
                title=self.form_title,
                widgets=widgets,
                appbuilder=self.appbuilder
            )

    def form_post(self, form):
        """
            Override this method to implement your form processing
        """
        pass

    def _get_edit_widget(self, form=None, exclude_cols=None, widgets=None):
        exclude_cols = exclude_cols or []
        widgets = widgets or {}
        widgets['edit'] = self.edit_widget(route_base=self.route_base,
                                           form=form,
                                           include_cols=self.form_columns,
                                           exclude_cols=exclude_cols,
                                           fieldsets=self.form_fieldsets
        )
        return widgets


class RestCRUDView(BaseCRUDView):
    """
        This class view exposes REST method for CRUD operations on you models
    """

    def _label_columns_json(self):
        ret = {}
        for key, value in list(self.label_columns.items()):
            ret[key] = str(value)
        return ret

    @expose('/api', methods=['GET'])
    def api(self):
        view_name = self.__class__.__name__
        api_urls = dict()
        api_urls['read'] = url_for(view_name + ".api_read")
        api_urls['delete'] = url_for(view_name + ".api_delete", pk="")
        api_urls['create'] = url_for(view_name + ".api_create")
        api_urls['update'] = url_for(view_name + ".api_update", pk="")
        modelview_urls = dict()
        modelview_urls['show'] = url_for(view_name + ".show", pk="")
        modelview_urls['add'] = url_for(view_name + ".add")
        modelview_urls['edit'] = url_for(view_name + ".edit", pk="")
        can_show = self.appbuilder.sm.has_access('can_show', view_name)
        can_edit = self.appbuilder.sm.has_access('can_edit', view_name)
        can_add = self.appbuilder.sm.has_access('can_add', view_name)
        can_delete = self.appbuilder.sm.has_access('can_delete', view_name)
        form_fields = {}
        search_filters = {}
        dict_filters = self._filters.get_search_filters()
        form = self.search_form.refresh()
        for col in self.search_columns:
            form_fields[col] = form[col]()
            search_filters[col] = [as_unicode(flt.name) for flt in dict_filters[col]]

        ret_json = jsonify(can_show = can_show,
                           can_add = can_add,
                           can_edit = can_edit,
                           can_delete = can_delete,
                        label_columns=self._label_columns_json(),
                        list_columns=self.list_columns,
                        order_columns=self.order_columns,
                        page_size=self.page_size,
                        modelview_name = view_name,
                        api_urls=api_urls,
                        search_filters=search_filters,
                        search_fields=form_fields,
                        modelview_urls=modelview_urls)
        response = make_response(ret_json, 200)
        response.headers['Content-Type'] = "application/json"
        return response


    @expose('/api/read', methods=['GET'])
    def api_read(self):
        """
            Parameters are passed as JSON with the following structure

            { 'order_colum':'<COLUMN_NAME>',
              'order_direction':'<asc|desc>',
              'page':'<PAGE NUMBER>',
              'page_size':'<PAGE SIZE>',
              'filter' : [['<COLUMN_NAME>','<FILTER TYPE>','<VALUE>']...]
            }
        """
        # Get arguments for ordering
        if get_order_args().get(self.__class__.__name__):
            order_column, order_direction = get_order_args().get(self.__class__.__name__)
        else:
            order_column, order_direction = '', ''
        page = get_page_args().get(self.__class__.__name__)
        page_size = get_page_size_args().get(self.__class__.__name__)
        get_filter_args(self._filters)
        joined_filters = self._filters.get_joined_filters(self._base_filters)
        count, lst = self.datamodel.query(joined_filters, order_column, order_direction, page=page, page_size=page_size)
        result = self.datamodel.get_values_json(lst, self.list_columns)
        pks = self.datamodel.get_keys(lst)
        ret_json = jsonify(label_columns=self._label_columns_json(),
                        list_columns=self.list_columns,
                        order_columns=self.order_columns,
                        page=page,
                        page_size=page_size,
                        count=count,
                        modelview_name=self.__class__.__name__,
                        pks = pks,
                        result=result)
        response = make_response(ret_json, 200)
        response.headers['Content-Type'] = "application/json"
        return response

    @expose('/api/create', methods=['POST'])
    def api_create(self):
        pass

    @expose('/api/update/<pk>', methods=['PUT'])
    def api_update(self, pk):
        pass

    @expose('/api/delete/<pk>', methods=['DELETE'])
    def api_delete(self, pk):
        item = self.datamodel.get(pk)
        self.pre_delete(item)
        self.datamodel.delete(item)
        self.post_delete(item)
        response = make_response(jsonify({'result': True}), 200)
        response.headers['Content-Type'] = "application/json"
        return response



class ModelView(RestCRUDView):
    """
        This is the CRUD generic view. If you want to automatically implement create, edit, delete, show, and list from your database tables, inherit your views from this class.

        Notice that this class inherits from BaseCRUDView and BaseModelView so all properties from the parent class can be overriden.
    """

    def __init__(self, **kwargs):
        super(ModelView, self).__init__(**kwargs)

    """
    --------------------------------
            LIST
    --------------------------------
    """
    @expose('/list/')
    @has_access
    def list(self):

        widgets = self._list()
        return self.render_template(self.list_template,
                               title=self.list_title,
                               widgets=widgets)

    """
    --------------------------------
            SHOW
    --------------------------------
    """

    @expose('/show/<pk>', methods=['GET'])
    @has_access
    def show(self, pk):

        widgets = self._show(pk)
        return self.render_template(self.show_template,
                               pk=pk,
                               title=self.show_title,
                               widgets=widgets,
                               related_views=self._related_views)

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
            return redirect(self.get_redirect())
        else:
            return self.render_template(self.add_template,
                                   title=self.add_title,
                                   widgets=widget)

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
            return redirect(self.get_redirect())
        else:
            return self.render_template(self.edit_template,
                                   title=self.edit_title,
                                   widgets=widgets,
                                   related_views=self._related_views)

    """
    ---------------------------
            DELETE
    ---------------------------
    """

    @expose('/delete/<pk>')
    @has_access
    def delete(self, pk):
        self._delete(pk)
        return redirect(self.get_redirect())


    @has_access
    @permission_name('list')
    @expose('/json')
    def json(self):
        if get_order_args().get(self.__class__.__name__):
            order_column, order_direction = get_order_args().get(self.__class__.__name__)
        else:
            order_column, order_direction = '', ''
        page = get_page_args().get(self.__class__.__name__)
        page_size = get_page_size_args().get(self.__class__.__name__)
        get_filter_args(self._filters)
        if not order_column and self.base_order:
            order_column, order_direction = self.base_order
        joined_filters = self._filters.get_joined_filters(self._base_filters)
        count, lst = self.datamodel.query(joined_filters, order_column, order_direction, page=page, page_size=page_size)
        result = [item.to_json() for item in lst]
        return jsonify(label_columns=self.label_columns,
                        include_columns=self.list_columns,
                        order_columns=self.order_columns,
                        page=page,
                        page_size=page_size,
                        count=count,
                        modelview_name=self.__class__.__name__,
                        result=result)


    @expose('/download/<string:filename>')
    @has_access
    def download(self, filename):
        return send_file(self.appbuilder.app.config['UPLOAD_FOLDER'] + filename,
                         attachment_filename=uuid_originalname(filename),
                         as_attachment=True)


    @expose('/action/<string:name>/<pk>', methods=['GET'])
    def action(self, name, pk):
        """
            Action method to handle actions from a show view
        """
        if self.appbuilder.sm.has_access(name, self.__class__.__name__):
            action = self.actions.get(name)
            return action.func(self.datamodel.get(pk))
        else:
            print("INVALID ACCESS ON {0}".format(self.__class__.__name__))
            flash(as_unicode(lazy_gettext("Access is Denied")), "danger")
            return redirect('.')


    @expose('/action_post', methods=['POST'])
    def action_post(self):
        """
            Action method to handle multiple records selected from a list view
        """
        name = request.form['action']
        pks = request.form.getlist('rowid')
        if self.appbuilder.sm.has_access(name, self.__class__.__name__):
            action = self.actions.get(name)
            items = [self.datamodel.get(pk) for pk in pks]
            return action.func(items)
        else:
            flash(as_unicode(lazy_gettext("Access is Denied")), "danger")
            return redirect('.')


class MasterDetailView(BaseCRUDView):
    """
        Implements behaviour for controlling two CRUD views
        linked by PK and FK, in a master/detail type with
        two lists.

        Master view will behave like a left menu::

            class DetailView(ModelView):
                datamodel = SQLAModel(DetailTable, db.session)

            class MasterView(MasterDetailView):
                datamodel = SQLAModel(MasterTable, db.session)
                related_views = [DetailView]

    """

    list_template = 'appbuilder/general/model/left_master_detail.html'
    list_widget = ListMasterWidget
    master_div_width = 2
    """
        Set to configure bootstrap class for master grid size
    """

    @expose('/list/')
    @expose('/list/<pk>')
    @has_access
    def list(self, pk=None):
        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()

        widgets = self._list()
        if pk:
            item = self.datamodel.get(pk)
            widgets = self._get_related_views_widgets(item, orders=orders,
                                                     pages=pages, page_sizes=page_sizes, widgets=widgets)
            related_views = self._related_views
        else:
            related_views = []

        return self.render_template(self.list_template,
                               title=self.list_title,
                               widgets=widgets,
                               related_views=related_views,
                               master_div_width=self.master_div_width)



class CompactCRUDMixin(BaseCRUDView):
    """
        Mix with ModelView to implement a list with add and edit on the same page.
    """
    _session_form_title = ''
    _session_form_widget = None
    _session_form_action = ''

    def _get_list_widget(self, **args):
        """ get joined base filter and current active filter for query """
        widgets = super(CompactCRUDMixin, self)._get_list_widget(**args)
        return {'list': GroupFormListWidget(list_widget=widgets.get('list'),
                                            form_widget=self._session_form_widget,
                                            form_action=self._session_form_action,
                                            form_title=self._session_form_title)}


    @expose('/list/', methods=['GET', 'POST'])
    @has_access
    def list(self):
        list_widgets = self._list()
        return self.render_template(self.list_template,
                               title=self.list_title,
                               widgets=list_widgets)

    @expose('/add/', methods=['GET', 'POST'])
    @has_access
    def add(self):
        widgets = self._add()
        if not widgets:
            self._session_form_action = ''
            self._session_form_widget = None
            return redirect(request.referrer)
        else:
            self._session_form_widget = widgets.get('add')
            self._session_form_action = request.url
            self._session_form_title = self.add_title
            return redirect(self.get_redirect())


    @expose('/edit/<pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk):
        widgets = self._edit(pk)
        if not widgets:
            self._session_form_action = ''
            self._session_form_widget = None

            return redirect(self.get_redirect())
        else:
            self._session_form_widget = widgets.get('edit')
            self._session_form_action = request.url
            self._session_form_title = self.edit_title
            return redirect(self.get_redirect())

"""
    This is for retro compatibility
"""
GeneralView = ModelView
