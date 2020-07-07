###############################################################################
# imports
from inspect import isclass
from flask import abort, request
from flask_appbuilder import ModelView, expose, has_access
from flask_appbuilder.widgets import (ListWidget, ListLinkWidget)
from flask_appbuilder.baseviews import log, BaseView
from flask_appbuilder.urltools import (
    get_page_args,
    get_page_size_args,
    get_order_args,
    get_filter_args
)
#from flask_appbuilder.security.decorators import 

###############################################################################
class CustomModelView(ModelView):

    #--------------------------------------------------------------------------
    def __init__(self, **kwargs):
        super(CustomModelView, self).__init__(**kwargs)

    #--------------------------------------------------------------------------
    @expose("/show/<pk>", methods=["GET"])
    @has_access
    def show(self, pk):
        pk = self._deserialize_pk_if_composite(pk)
        search_widgets = []
        widgets = self._show_search(pk)

        

        return self.render_template(
            self.show_template,
            pk=pk,
            title=self.show_title,
            widgets=widgets,
            related_views=self._related_views,
        )

    #--------------------------------------------------------------------------
    def _show_search(self, pk):
        """
            show function logic, override to implement different logic
            returns show and related list widget
        """
        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()

        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            abort(404)
        widgets = self._get_show_widget(pk, item)

        self.update_redirect()
        return self._get_related_views_widgets_search(
            item, orders=orders, pages=pages, page_sizes=page_sizes, widgets=widgets
        )

    """
    -----------------------------------------------------
            GET WIDGETS SECTION
    -----------------------------------------------------
    """

    def _get_related_view_widget_search(
        self,
        item,
        related_view,
        order_column="",
        order_direction="",
        page=None,
        page_size=None,
        search_filters=None,
    ):

        fk = related_view.datamodel.get_related_fk(self.datamodel.obj)
        filters = related_view.datamodel.get_filters()

        if search_filters:
            try:
                filters = filters.get_joined_filters(search_filters)
            except:
                pass

        # Check if it's a many to one model relation
        if related_view.datamodel.is_relation_many_to_one(fk):
            filters.add_filter_related_view(
                fk,
                self.datamodel.FilterRelationOneToManyEqual,
                self.datamodel.get_pk_value(item),
            )
        # Check if it's a many to many model relation
        elif related_view.datamodel.is_relation_many_to_many(fk):
            filters.add_filter_related_view(
                fk,
                self.datamodel.FilterRelationManyToManyEqual,
                self.datamodel.get_pk_value(item),
            )
        else:
            if isclass(related_view) and issubclass(related_view, BaseView):
                name = related_view.__name__
            else:
                name = related_view.__class__.__name__
            log.error("Can't find relation on related view {0}".format(name))
            return None

        

        return related_view._get_view_widget(
            filters=filters,
            order_column=order_column,
            order_direction=order_direction,
            page=page,
            page_size=page_size,
        )

    def _get_related_views_widgets_search(
        self, item, orders=None, pages=None, page_sizes=None, widgets=None, **args
    ):
        """
            :return:
                Returns a dict with 'related_views' key with a list of
                Model View widgets
        """
        widgets = widgets or {}
        widgets["related_views"] = []
        widgets["search_widgets"] = []

        for view in self._related_views:

            try:
                
                validSearchRule = True
                for arg in request.args:
                    if "None" in request.args.get(arg):
                        validSearchRule = False
                if validSearchRule:  
                    get_filter_args(view._filters)
                
                 
            except:
                pass

            if orders.get(view.__class__.__name__):
                order_column, order_direction = orders.get(view.__class__.__name__)
            else:
                order_column, order_direction = "", ""

            form = view.search_form.refresh()
            self._get_search_widget_search(form=form, 
                                           widgets=widgets, 
                                           filters=view._filters,
                                           search_columns=view.search_columns,
                                           route_base=view.route_base)

            

            widgets["related_views"].append(
                self._get_related_view_widget_search(
                    item,
                    view,
                    order_column,
                    order_direction,
                    page=pages.get(view.__class__.__name__),
                    page_size=page_sizes.get(view.__class__.__name__),
                    search_filters=view._filters
                )
            )
        return widgets

    #--------------------------------------------------------------------------
    def _get_search_widget_search(self, form=None, exclude_cols=None, widgets=None, filters=None, search_columns=None, route_base=None):
        exclude_cols = exclude_cols or []
        widgets = widgets or {}

        if not "search_widgets" in widgets:
            widgets["search_widgets"] = list()

        widgets["search_widgets"].append(
            self.search_widget(
                route_base=self.route_base, # TODO ??
                form=form,
                include_cols=search_columns,
                exclude_cols=exclude_cols,
                filters=filters,
            )
        )
        return widgets
    
