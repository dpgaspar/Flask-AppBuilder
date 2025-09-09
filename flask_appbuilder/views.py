import logging
import os.path as op

from flask import (
    current_app,
    flash,
    redirect,
    request,
    send_file,
    session,
)
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.baseviews import (
    BaseCRUDView,
    BaseFormView,
    BaseView,
    expose,
)
from flask_appbuilder.const import FLAMSG_ERR_SEC_ACCESS_DENIED, PERMISSION_PREFIX
from flask_appbuilder.exceptions import FABException
from flask_appbuilder.filemanager import uuid_originalname
from flask_appbuilder.security.decorators import (
    has_access,
)
from flask_appbuilder.urltools import (
    get_order_args,
    get_page_args,
    get_page_size_args,
)
from flask_appbuilder.widgets import GroupFormListWidget, ListMasterWidget


log = logging.getLogger(__name__)


class IndexView(BaseView):
    """
    A simple view that implements the index for the site
    """

    route_base = ""
    default_view = "index"
    index_template = "appbuilder/index.html"

    @expose("/")
    def index(self):
        self.update_redirect()
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class UtilView(BaseView):
    """
    A simple view that implements special util routes.
    At the moment it only supports the back special endpoint.
    """

    route_base = ""
    default_view = "back"

    @expose("/back")
    def back(self):
        return redirect(self.get_redirect())


class SimpleFormView(BaseFormView):
    """
    View for presenting your own forms
    Inherit from this view to provide some base processing
    for your customized form views.

    Notice that this class inherits from BaseView so all properties
    from the parent class can be overridden also.

    Implement form_get and form_post to implement your
    form pre-processing and post-processing
    """

    @expose("/form", methods=["GET"])
    @has_access
    def this_form_get(self):
        self._init_vars()
        form = self.form.refresh()

        self.form_get(form)
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return self.render_template(
            self.form_template,
            title=self.form_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
        )

    @expose("/form", methods=["POST"])
    @has_access
    def this_form_post(self):
        self._init_vars()
        form = self.form.refresh()

        if form.validate_on_submit():
            response = self.form_post(form)
            if not response:
                return redirect(self.get_redirect())
            return response
        else:
            widgets = self._get_edit_widget(form=form)
            return self.render_template(
                self.form_template,
                title=self.form_title,
                widgets=widgets,
                appbuilder=self.appbuilder,
            )


class PublicFormView(BaseFormView):
    """
    View for presenting your own forms
    Inherit from this view to provide some base
    processing for your customized form views.

    Notice that this class inherits from BaseView
    so all properties from the parent class can be overridden also.

    Implement form_get and form_post to implement
    your form pre-processing and post-processing
    """

    @expose("/form", methods=["GET"])
    def this_form_get(self):
        self._init_vars()
        form = self.form.refresh()
        self.form_get(form)
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return self.render_template(
            self.form_template,
            title=self.form_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
        )

    @expose("/form", methods=["POST"])
    def this_form_post(self):
        self._init_vars()
        form = self.form.refresh()
        if form.validate_on_submit():
            response = self.form_post(form)
            if not response:
                return redirect(self.get_redirect())
            return response
        else:
            widgets = self._get_edit_widget(form=form)
            return self.render_template(
                self.form_template,
                title=self.form_title,
                widgets=widgets,
                appbuilder=self.appbuilder,
            )


class ModelView(BaseCRUDView):
    """
    This is the CRUD generic view.
    If you want to automatically implement create, edit,
    delete, show, and list from your database tables,
    inherit your views from this class.

    Notice that this class inherits from BaseCRUDView and BaseModelView
    so all properties from the parent class can be overridden.
    """

    def __init__(self, **kwargs):
        super(ModelView, self).__init__(**kwargs)

    def post_add_redirect(self):
        """Override this function to control the
        redirect after add endpoint is called."""
        return redirect(self.get_redirect())

    def post_edit_redirect(self):
        """Override this function to control the
        redirect after edit endpoint is called."""
        return redirect(self.get_redirect())

    def post_delete_redirect(self):
        """Override this function to control the
        redirect after edit endpoint is called."""
        return redirect(self.get_redirect())

    """
    --------------------------------
            LIST
    --------------------------------
    """

    @expose("/list/")
    @has_access
    def list(self):
        self.update_redirect()
        try:
            widgets = self._list()
        except FABException as exc:
            flash(f"An error occurred: {exc}", "warning")
            return redirect(self.get_redirect())
        return self.render_template(
            self.list_template, title=self.list_title, widgets=widgets
        )

    """
    --------------------------------
            SHOW
    --------------------------------
    """

    @expose("/show/<pk>", methods=["GET"])
    @has_access
    def show(self, pk):
        pk = self._deserialize_pk_if_composite(pk)
        widgets = self._show(pk)
        return self.render_template(
            self.show_template,
            pk=pk,
            title=self.show_title,
            widgets=widgets,
            related_views=self._related_views,
        )

    """
    ---------------------------
            ADD
    ---------------------------
    """

    @expose("/add", methods=["GET", "POST"])
    @has_access
    def add(self):
        widget = self._add()
        if not widget:
            return self.post_add_redirect()
        else:
            return self.render_template(
                self.add_template, title=self.add_title, widgets=widget
            )

    """
    ---------------------------
            EDIT
    ---------------------------
    """

    @expose("/edit/<pk>", methods=["GET", "POST"])
    @has_access
    def edit(self, pk):
        pk = self._deserialize_pk_if_composite(pk)
        widgets = self._edit(pk)
        if not widgets:
            return self.post_edit_redirect()
        else:
            return self.render_template(
                self.edit_template,
                title=self.edit_title,
                widgets=widgets,
                related_views=self._related_views,
            )

    """
    ---------------------------
            DELETE
    ---------------------------
    """

    @expose("/delete/<pk>", methods=["GET", "POST"])
    @has_access
    def delete(self, pk):
        # Maintains compatibility but refuses to delete on GET methods if CSRF is enabled
        if not self.is_get_mutation_allowed():
            self.update_redirect()
            log.warning("CSRF is enabled and a delete using GET was invoked")
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            return self.post_delete_redirect()
        pk = self._deserialize_pk_if_composite(pk)
        self._delete(pk)
        return self.post_delete_redirect()

    @expose("/download/<string:filename>")
    @has_access
    def download(self, filename):
        return send_file(
            op.join(current_app.config["UPLOAD_FOLDER"], filename),
            download_name=uuid_originalname(filename),
            as_attachment=True,
        )

    def get_action_permission_name(self, name: str) -> str:
        """
        Get the permission name of an action name
        """
        _permission_name = self.method_permission_name.get(
            self.actions.get(name).func.__name__
        )
        if _permission_name:
            return PERMISSION_PREFIX + _permission_name
        else:
            return name

    @expose("/action/<string:name>/<pk>", methods=["GET", "POST"])
    def action(self, name, pk):
        """
        Action method to handle actions from a show view
        """
        # Maintains compatibility but refuses to proceed if CSRF is enabled
        if not self.is_get_mutation_allowed():
            self.update_redirect()
            log.warning("CSRF is enabled and a action using GET was invoked")
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            return redirect(self.get_redirect())

        pk = self._deserialize_pk_if_composite(pk)
        permission_name = self.get_action_permission_name(name)
        if self.appbuilder.sm.has_access(permission_name, self.class_permission_name):
            action = self.actions.get(name)
            return action.func(self.datamodel.get(pk))
        else:
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            return redirect(".")

    @expose("/action_post", methods=["POST"])
    def action_post(self):
        """
        Action method to handle multiple records selected from a list view
        """
        name = request.form["action"]
        pks = request.form.getlist("rowid")
        permission_name = self.get_action_permission_name(name)

        if self.appbuilder.sm.has_access(permission_name, self.class_permission_name):
            action = self.actions.get(name)
            items = [
                self.datamodel.get(self._deserialize_pk_if_composite(pk)) for pk in pks
            ]
            return action.func(items)
        else:
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            return redirect(".")


class MasterDetailView(BaseCRUDView):
    """
    Implements behaviour for controlling two CRUD views
    linked by PK and FK, in a master/detail type with
    two lists.

    Master view will behave like a left menu::

        class DetailView(ModelView):
            datamodel = SQLAInterface(DetailTable, db.session)

        class MasterView(MasterDetailView):
            datamodel = SQLAInterface(MasterTable, db.session)
            related_views = [DetailView]

    """

    list_template = "appbuilder/general/model/left_master_detail.html"
    list_widget = ListMasterWidget
    master_div_width = 2
    """
        Set to configure bootstrap class for master grid size
    """

    @expose("/list/")
    @expose("/list/<pk>")
    @has_access
    def list(self, pk=None):
        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()

        widgets = self._list()
        if pk:
            item = self.datamodel.get(pk)
            widgets = self._get_related_views_widgets(
                item, orders=orders, pages=pages, page_sizes=page_sizes, widgets=widgets
            )
            related_views = self._related_views
        else:
            related_views = []

        return self.render_template(
            self.list_template,
            title=self.list_title,
            widgets=widgets,
            related_views=related_views,
            master_div_width=self.master_div_width,
        )


class MultipleView(BaseView):
    """
    Use this view to render multiple views on the same page,
    exposed on the list endpoint.

    example (after defining GroupModelView and ContactModelView)::

        class MultipleViewsExp(MultipleView):
            views = [GroupModelView, ContactModelView]

    """

    list_template = "appbuilder/general/model/multiple_views.html"
    """ Override this to implement your own template for the list endpoint """

    views = None
    " A list of ModelView's to render on the same page "
    _views = None

    def __init__(self, **kwargs):
        super(MultipleView, self).__init__(**kwargs)
        self.views = self.views or list()
        self._views = self._views or list()

    def get_uninit_inner_views(self):
        return self.views

    def get_init_inner_views(self):
        return self._views

    @expose("/list/")
    @has_access
    def list(self):
        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()
        views_widgets = list()
        for view in self._views:
            if orders.get(view.__class__.__name__):
                order_column, order_direction = orders.get(view.__class__.__name__)
            else:
                order_column, order_direction = "", ""
            page = pages.get(view.__class__.__name__)
            page_size = page_sizes.get(view.__class__.__name__)
            views_widgets.append(
                view._get_view_widget(
                    filters=view._base_filters,
                    order_column=order_column,
                    order_direction=order_direction,
                    page=page,
                    page_size=page_size,
                )
            )
        self.update_redirect()
        return self.render_template(
            self.list_template, views=self._views, views_widgets=views_widgets
        )


class CompactCRUDMixin(BaseCRUDView):
    """
    Mix with ModelView to implement a list with add and edit on the same page.
    """

    @classmethod
    def set_key(cls, k, v):
        """Allows attaching stateless information to the class using the
        flask session dict
        """
        k = cls.__name__ + "__" + k
        session[k] = v

    @classmethod
    def get_key(cls, k, default=None):
        """Matching get method for ``set_key``"""
        k = cls.__name__ + "__" + k
        if k in session:
            return session[k]
        else:
            return default

    @classmethod
    def del_key(cls, k):
        """Matching get method for ``set_key``"""
        k = cls.__name__ + "__" + k
        session.pop(k)

    def _get_list_widget(self, **kwargs):
        """get joined base filter and current active filter for query"""
        widgets = super(CompactCRUDMixin, self)._get_list_widget(**kwargs)
        session_form_widget = self.get_key("session_form_widget", None)

        form_widget = None
        if session_form_widget == "add":
            form_widget = self._add().get("add")
        elif session_form_widget == "edit":
            pk = self.get_key("session_form_edit_pk")
            if pk and self.datamodel.get(int(pk)):
                form_widget = self._edit(int(pk)).get("edit")
        return {
            "list": GroupFormListWidget(
                list_widget=widgets.get("list"),
                form_widget=form_widget,
                form_action=self.get_key("session_form_action", ""),
                form_title=self.get_key("session_form_title", ""),
            )
        }

    @expose("/list/", methods=["GET", "POST"])
    @has_access
    def list(self):
        list_widgets = self._list()
        return self.render_template(
            self.list_template, title=self.list_title, widgets=list_widgets
        )

    @expose("/add/", methods=["GET", "POST"])
    @has_access
    def add(self):
        widgets = self._add()
        if not widgets:
            self.set_key("session_form_action", "")
            self.set_key("session_form_widget", None)
            return redirect(request.referrer)
        else:
            self.set_key("session_form_widget", "add")
            self.set_key("session_form_action", request.script_root + request.full_path)
            self.set_key("session_form_title", self.add_title)
            return redirect(self.get_redirect())

    @expose("/edit/<pk>", methods=["GET", "POST"])
    @has_access
    def edit(self, pk):
        pk = self._deserialize_pk_if_composite(pk)
        widgets = self._edit(pk)
        self.update_redirect()
        if not widgets:
            self.set_key("session_form_action", "")
            self.set_key("session_form_widget", None)
            return redirect(self.get_redirect())
        else:
            self.set_key("session_form_widget", "edit")
            self.set_key("session_form_action", request.script_root + request.full_path)
            self.set_key("session_form_title", self.add_title)
            self.set_key("session_form_edit_pk", pk)
            return redirect(self.get_redirect())

    @expose("/delete/<pk>", methods=["GET", "POST"])
    @has_access
    def delete(self, pk):
        # Maintains compatibility but refuses to delete on GET methods if CSRF is enabled
        if not self.is_get_mutation_allowed():
            self.update_redirect()
            log.warning("CSRF is enabled and a delete using GET was invoked")
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            return redirect(self.get_redirect())

        pk = self._deserialize_pk_if_composite(pk)
        self._delete(pk)
        edit_pk = self.get_key("session_form_edit_pk")
        if pk == edit_pk:
            self.del_key("session_form_edit_pk")
        return redirect(self.get_redirect())


"""
    This is for retro compatibility
"""
GeneralView = ModelView
