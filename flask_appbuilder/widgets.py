'''
Created on Oct 12, 2013

@author: Daniel Gaspar
'''

from flask.globals import _request_ctx_stack


class RenderTemplateWidget(object):

    template = 'appbuilder/general/widgets/render.html'

    def __call__(self, **kwargs):
        ctx = _request_ctx_stack.top
        jinja_env = ctx.app.jinja_env

        template = jinja_env.get_template(self.template)
        return template.render(kwargs)


class FormWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/form.html'

    route_base = ''
    form = None
    include_cols = []
    exclude_cols = []
    fieldsets = []

    def __init__(self, route_base='', form = None, include_cols = [], exclude_cols=[], fieldsets = [], **kwargs):
        self.route_base = route_base
        self.form = form
        self.include_cols = include_cols
        self.exclude_cols = exclude_cols
        self.fieldsets = fieldsets

    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['form'] = self.form
        kwargs['include_cols'] = self.include_cols
        kwargs['exclude_cols'] = self.exclude_cols
        kwargs['fieldsets'] = self.fieldsets
        return super(FormWidget, self).__call__(**kwargs)


class SearchWidget(FormWidget):
    template = 'appbuilder/general/widgets/search.html'
    filters = None
    
    def __init__(self, **kwargs):
        self.filters = kwargs.get('filters')
        return super(SearchWidget, self).__init__(**kwargs)

    def __call__(self, **kwargs):
        """ create dict labels based on form """
        """ create dict of form widgets """
        """ create dict of possible filters """
        """ create list of active filters """
        label_columns = {}
        form_fields = {}
        search_filters = {}
        dict_filters = self.filters.get_search_filters()
        for col in self.include_cols:
            label_columns[col] = unicode(self.form[col].label.text)
            form_fields[col] = self.form[col]()
            search_filters[col] = [unicode(flt.name) for flt in dict_filters[col]]                

        kwargs['label_columns'] = label_columns
        kwargs['form_fields'] = form_fields
        kwargs['search_filters'] = search_filters
        kwargs['active_filters'] = self.filters.get_filters_values_tojson()
        
        return super(SearchWidget, self).__call__(**kwargs)

class ShowWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/show.html'

    route_base = ''
    pk = None
    label_columns = []
    include_columns = []
    value_columns = []
    actions = None
    fieldsets = []

    def __init__(self, route_base = '',
                pk = None,
                label_columns = [],
                include_columns = [],
                value_columns = [],
                actions = None,
                fieldsets = []):
        self.route_base = route_base
        self.pk = pk
        self.label_columns = label_columns
        self.include_columns = include_columns
        self.value_columns = value_columns
        self.actions = actions
        self.fieldsets = fieldsets

    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['pk'] = self.pk
        kwargs['label_columns'] = self.label_columns
        kwargs['include_columns'] = self.include_columns
        kwargs['value_columns'] = self.value_columns
        kwargs['actions'] = self.actions
        kwargs['fieldsets'] = self.fieldsets
        return super(ShowWidget, self).__call__(**kwargs)


class ListWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/list.html'

    route_base = ''
    label_columns = []
    include_columns = []
    value_columns = []
    order_columns = []
    page = None
    page_size = None
    count = 0
    pks = []
    actions = None
    filters = {}
    generalview_name = ''

    def __init__(self, route_base = '',
                 label_columns = [],
                 include_columns = [],
                 value_columns = [],
                 order_columns = [],
                 page = None,
                 page_size = None,
                 count = 0,
                 pks = [],
                 actions = None,
                 filters = {},
                 generalview_name = ''):
        self.route_base = route_base
        self.label_columns = label_columns
        self.include_columns = include_columns
        self.value_columns = value_columns
        self.order_columns = order_columns
        self.page = page
        self.page_size = page_size
        self.count = count
        self.pks = pks
        self.actions = actions
        self.filters = filters
        self.generalview_name = generalview_name

    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['label_columns'] = self.label_columns
        kwargs['include_columns'] = self.include_columns
        kwargs['value_columns'] = self.value_columns
        kwargs['order_columns'] = self.order_columns
        
        kwargs['page'] = self.page
        kwargs['page_size'] = self.page_size
        kwargs['count'] = self.count
        
        kwargs['pks'] = self.pks
        kwargs['actions'] = self.actions
        kwargs['filters'] = self.filters
        kwargs['generalview_name'] = self.generalview_name
        return super(ListWidget, self).__call__(**kwargs)
        
class ListThumbnail(ListWidget):
    template = 'appbuilder/general/widgets/list_thumbnail.html'

class ListCarousel(ListWidget):
    template = 'appbuilder/general/widgets/list_carousel.html'

class ListItem(ListWidget):
    template = 'appbuilder/general/widgets/list_item.html'

class ListBlock(ListWidget):
    template = 'appbuilder/general/widgets/list_block.html'
