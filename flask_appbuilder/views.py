import logging
from flask import render_template, flash, redirect, send_file, jsonify
from .filemanager import uuid_originalname
from .security.decorators import has_access, permission_name
from .widgets import FormWidget, GroupFormListWidget, ListMasterWidget
from .baseviews import expose, BaseView, BaseModelView, BaseCRUDView
from .models.group import GroupByProcessData
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
        return render_template(self.index_template, appbuilder=self.appbuilder)

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
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return render_template(self.form_template,
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
            return render_template(
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

    def _get_edit_widget(self, form=None, exclude_cols=[], widgets={}):
        widgets['edit'] = self.edit_widget(route_base=self.route_base,
                                           form=form,
                                           include_cols=self.form_columns,
                                           exclude_cols=exclude_cols,
                                           fieldsets=self.form_fieldsets
        )
        return widgets


class ModelView(BaseCRUDView):
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
        return render_template(self.list_template,
                               title=self.list_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder)

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
                               pk=pk,
                               title=self.show_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder,
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
            return render_template(self.add_template,
                                   title=self.add_title,
                                   widgets=widget,
                                   appbuilder=self.appbuilder)

    @has_access
    @permission_name('add')
    @expose('/add_post', methods=['POST'])
    def add_post(self):
        get_filter_args(self._filters)
        exclude_cols = self._filters.get_relation_cols()

        item = self.datamodel.obj()
        form = self.add_form.refresh()
        form.populate_obj(item)
        widget = self._get_add_widget(form=form, exclude_cols=exclude_cols)
        return render_template(self.add_template,
                                   title=self.add_title,
                                   widgets=widget,
                                   appbuilder=self.appbuilder)


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
            return render_template(self.edit_template,
                                   title=self.edit_title,
                                   widgets=widgets,
                                   appbuilder=self.appbuilder,
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


    @expose('/action/<string:name>/<pk>')
    @has_access
    def action(self, name, pk):
        if self.appbuilder.sm.has_access(name, self.__class__.__name__):
            action = self.actions.get(name)
            return action.func(self.datamodel.get(pk))
        else:
            flash("Access is Denied %s %s" % (name, self.__class__.__name__), "danger")
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

        return render_template(self.list_template,
                               title=self.list_title,
                               widgets=widgets,
                               related_views=related_views,
                               master_div_width=self.master_div_width,
                               appbuilder=self.appbuilder)



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
        return render_template(self.list_template,
                               title=self.list_title,
                               widgets=list_widgets,
                               appbuilder=self.appbuilder)

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
