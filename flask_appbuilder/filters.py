from app import app
from flask.ext.appbuilder.security.models import is_menu_public, is_item_public
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask import g, request, url_for
from flask.ext.login import current_user


def app_template_filter(filter_name=''):
    """
        Use this decorator to expose views in your view classes.
    """
    def wrap(f):
        if not hasattr(f, '_filter'):
            f._filter = filter_name
        return f
    return wrap


class TemplateFilters(object):
    
    def __init__(self, app):
        for attr_name in dir(self):
            if hasattr(getattr(self, attr_name),'_filter'):
                attr = getattr(self, attr_name)
                app.jinja_env.filters[attr._filter] = attr


    @app_template_filter('link_order')
    def link_order_filter(self, item):
        new_args = request.view_args.copy()
        args = request.args.copy()
        if ('order_column') in args:
            if request.view_args.get('order_direction') == 'asc':
                args['order_direction'] = 'desc'
            else:
                args['order_direction'] = 'asc'
        else:
            print new_args, args
            args['order_column'] = item
            args['order_direction'] = 'asc'
        return url_for(request.endpoint,**dict(new_args.items() + args.to_dict().items()))



    @app_template_filter('link_order2')
    def link_order_filter2(self, s):

        order_column = request.args.get('order_column')
        if order_column:
            lststr = request.url.split('order_column')
            if (request.args.get('order_direction') == 'asc'):
                if len(request.args) > 0:
                    return lststr[0] + 'order_column=' + s + '&order_direction=desc'
                else:
                    return lststr[0] + '&order_column=' + s + '&order_direction=desc'
            else:
                if len(request.args) > 0:
                    return  lststr[0] + 'order_column=' + s + '&order_direction=asc'
                else:
                    return  lststr[0] + '&order_column=' + s + '&order_direction=asc'
        else:
            if len(request.args) > 0:
                return  request.url + '&order_column=' + s + '&order_direction=asc'
            else:
                return  request.url + '?order_column=' + s + '&order_direction=asc'


    @app_template_filter('link_page')
    def link_page_filter(self, s):

        page = request.args.get('page')
        if page:
            lststr = request.url.split('page')
            if len(request.args) > 0:
                return  lststr[0] + 'page=' + str(s)
            else:
                return  lststr[0] + '?page=' + str(s)
        else:
            if len(request.args) > 0:
                return  request.url + '&page=' + str(s)
            else:
                return  request.url + '?page=' + str(s)
                

    @app_template_filter('get_link_next')
    def get_link_next_filter(self, s):
        return request.args.get('next')


    @app_template_filter('set_link_filters')
    def add_link_filters_filter(self, path, filters):
        lnkstr = path
        for _filter in filters:
            try:
                datamodel = SQLAModel(filters.get(_filter))
                pk_name = datamodel.get_pk_name()
                pk_value = getattr(filters.get(_filter), pk_name)
                lnkstr = lnkstr + '&_flt_' + _filter + '=' + str(pk_value)
            except:
                pass
        return lnkstr

    @app_template_filter('get_link_order')
    def get_link_order_filter(self, s):
        if request.args.get('order_column') == s:
            order_direction = request.args.get('order_direction')
            if (order_direction):
                if (order_direction == 'asc'):
                    return 2
                else:
                    return 1
        else:
            return 0

    @app_template_filter('get_attr')
    def get_attr_filter(self, obj, item):
        return getattr(obj, item)


    @app_template_filter('is_menu_visible')
    def is_menu_visible(self, item):
        if current_user.is_authenticated():
            if is_menu_public(item) or g.user.has_menu_access(item.name):
                return True
            else:
                return False
        else:
            if is_menu_public(item.name):
                return True
            else:
                return False

    @app_template_filter('is_item_visible')
    def is_item_visible(self, permission, item):
        if current_user.is_authenticated():
            if g.user.has_permission_on_view(permission, item):
                return True
            else:
                return False
        else:
            if is_item_public(permission, item):
                return True
            else:
                return False
