from app import app
from flask.ext.appbuilder.security.models import is_menu_public, is_item_public
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask import g, request
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
    def link_order_filter(self, s):

        if (request.args.get('order_column') == s):
            lststr = request.path.split('?')
            if (request.args.get('order_direction') == 'asc'):
                return lststr[0] + '?order_column=' + s + '&order_direction=desc'
            else:
                return  request.path + '?order_column=' + s + '&order_direction=asc'
        else:
            return  request.path + '?order_column=' + s + '&order_direction=asc'



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
