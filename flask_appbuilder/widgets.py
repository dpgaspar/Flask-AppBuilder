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
    exclude_cols = []
    fieldsets = []

    def __init__(self, route_base='', form=None, exclude_cols=[], fieldsets = []):
        self.route_base = route_base
        self.form = form
        self.exclude_cols = exclude_cols
        self.fieldsets = fieldsets


    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['form'] = self.form
        kwargs['exclude_cols'] = self.exclude_cols
        kwargs['fieldsets'] = self.fieldsets
        return super(FormWidget, self).__call__(**kwargs)

class SearchWidget(FormWidget):
    template = 'appbuilder/general/widgets/search.html'
    def __init__(self, **kwargs):
        return super(SearchWidget, self).__init__(**kwargs)

class ShowWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/show.html'

    route_base = ''
    pk = None
    label_columns = []
    include_columns = []
    value_columns = []
    additional_links = []
    fieldsets = []

    def __init__(self, route_base = '',
                pk = None,
                label_columns = [],
                include_columns = [],
                value_columns = [],
                additional_links = [],
                fieldsets = []):
        self.route_base = route_base
        self.pk = pk
        self.label_columns = label_columns
        self.include_columns = include_columns
        self.value_columns = value_columns
        self.additional_links = additional_links
        self.fieldsets = fieldsets

    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['pk'] = self.pk
        kwargs['label_columns'] = self.label_columns
        kwargs['include_columns'] = self.include_columns
        kwargs['value_columns'] = self.value_columns
        kwargs['additional_links'] = self.additional_links
        kwargs['fieldsets'] = self.fieldsets
        return super(ShowWidget, self).__call__(**kwargs)


class ListWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/list.html'

    route_base = ''
    label_columns = []
    include_columns = []
    value_columns = []
    order_columns = []
    pks = []
    filters = {}
    generalview_name = ''

    def __init__(self, route_base = '',
                 label_columns = [],
                 include_columns = [],
                 value_columns = [],
                 order_columns = [],
                 pks = [],
                 filters = {},
                 generalview_name = ''):
        self.route_base = route_base
        self.label_columns = label_columns
        self.include_columns = include_columns
        self.value_columns = value_columns
        self.order_columns = order_columns
        self.pks = pks
        self.filters = filters
        self.generalview_name = generalview_name

    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['label_columns'] = self.label_columns
        kwargs['include_columns'] = self.include_columns
        kwargs['value_columns'] = self.value_columns
        kwargs['order_columns'] = self.order_columns
        kwargs['pks'] = self.pks
        kwargs['filters'] = self.filters
        kwargs['generalview_name'] = self.generalview_name
        return super(ListWidget, self).__call__(**kwargs)
        
class ListThumbnail(ListWidget):
    template = 'appbuilder/general/widgets/list_thumbnail.html'
