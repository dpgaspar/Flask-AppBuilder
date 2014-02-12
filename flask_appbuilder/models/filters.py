import logging
from flask.ext.babelpkg import lazy_gettext

log = logging.getLogger(__name__)

class BaseFilter(object):

    column_name = ''
    datamodel = None
    model = None
    name = ''
    is_related_view = False
    """ 
        Sets this filter to a special kind of filter for related views.
        If true this filter was not set by the user
    """

    def __init__(self, column_name, datamodel, is_related_view = False):
        """
            Constructor.

            :param column_name:
                Model field name
            :param datamodel:
                The datamodel access class
            :param is_related_view:
                Optional internal parameter to filter related views
        """
        self.column_name = column_name
        self.datamodel = datamodel
        self.model = datamodel.obj
        self.is_related_view = is_related_view
    
    def apply(self, query, value):
        """
            Override this to implement you own new filters
        """
        pass
        
    def __repr__(self):
        return self.name

class FilterStartsWith(BaseFilter):
    name = lazy_gettext('Starts with')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like(value + '%'))

class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext('Not Starts with')
    
    def apply(self, query, value):
        return query.filter(~getattr(self.model,self.column_name).like(value + '%'))

class FilterEndsWith(BaseFilter):
    name = lazy_gettext('Ends with')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like('%' + value))

class FilterNotEndsWith(BaseFilter):
    name = lazy_gettext('Not Ends with')
    
    def apply(self, query, value):
        return query.filter(~getattr(self.model,self.column_name).like('%' + value))

class FilterContains(BaseFilter):
    name = lazy_gettext('Contains')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like('%' + value + '%'))

class FilterNotContains(BaseFilter):
    name = lazy_gettext('Not Contains')
    
    def apply(self, query, value):
        return query.filter(~getattr(self.model,self.column_name).like('%' + value + '%'))


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) == value)

class FilterNotEqual(BaseFilter):
    name = lazy_gettext('Not Equal to')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) != value)


class FilterGreater(BaseFilter):
    name = lazy_gettext('Greater than')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) > value)
        
class FilterSmaller(BaseFilter):
    name = lazy_gettext('Smaller than')
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) < value)

class FilterRelation(BaseFilter):
    pass

class FilterRelationOneToManyEqual(FilterRelation):
    name = lazy_gettext('Relation')
    
    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model,self.column_name) == rel_obj)

class FilterRelationOneToManyNotEqual(FilterRelation):
    name = lazy_gettext('No Relation')
    
    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model,self.column_name) != rel_obj)

    
class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext('Relation as Many')
    
    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model,self.column_name).contains(item))

class FilterEqualFunction(BaseFilter):
    name = "Filter view with a function"
    
    def apply(self, query, func):
        return query.filter(getattr(self.model,self.column_name) == func())


class Filters(object):
    
    filters = []
    """ List of instanciated filters """
    values = []
    """ list of values to apply to filters """
    _search_filters = {}
    """ dict like {'col_name':[BaseFilter1, BaseFilter2, ...], ... } """
    _all_filters = {}

    def __init__(self, search_columns = [], datamodel = None):
        self.clear_filters()
        if search_columns and datamodel:
            self._search_filters = self._get_filters(search_columns, datamodel)
            self._all_filters = self._get_filters(datamodel.get_columns_list(), datamodel)
        
    def get_search_filters(self):
        return self._search_filters

    def _get_filters(self, cols, datamodel):
        filters = {}
        for col in cols:
            lst_flt = self._get_filter_type(col, datamodel)
            if lst_flt:
                filters[col] = lst_flt
        return filters

    def _get_filter_type(self, col, datamodel):
        prop = datamodel.get_col_property(col)
        if datamodel.is_relation(prop):
            if datamodel.is_relation_many_to_one(prop):
                return [FilterRelationOneToManyEqual(col, datamodel),
                        FilterRelationOneToManyNotEqual(col, datamodel)]
            elif datamodel.is_relation_many_to_many(prop):
                return [FilterRelationManyToManyEqual(col, datamodel)]
        else:
            if datamodel.is_text(col) or datamodel.is_string(col):
                return [FilterStartsWith(col, datamodel), 
                    FilterEndsWith(col, datamodel), 
                    FilterContains(col, datamodel), 
                    FilterEqual(col, datamodel),
                    FilterNotStartsWith(col, datamodel),
                    FilterNotEndsWith(col, datamodel),
                    FilterNotContains(col, datamodel),
                    FilterNotEqual(col, datamodel),]    
            elif datamodel.is_integer(col) or datamodel.is_date(col) or datamodel.is_datetime(col):
                return [FilterEqual(col, datamodel),
                    FilterGreater(col, datamodel), 
                    FilterSmaller(col, datamodel),
                    FilterNotEqual(col, datamodel)]
            else:
                log.warning('Filter type not supported for column: %s' % (col))
                return None

    def clear_filters(self):
        self.filters = []
        self.values = []

    def add_filter_index(self, column_name, filter_instance_index, value):
        self._add_filter(self._all_filters[column_name][filter_instance_index], value)
    
    def add_filter(self, column_name, filter_class, datamodel, value):
        self._add_filter(filter_class(column_name, datamodel), value)
        return self

    def add_filter_related_view(self, column_name, filter_class, datamodel, value):
        self._add_filter(filter_class(column_name, datamodel, True), value)
        return self

    def add_filter_list(self, datamodel, active_filter_list = None):
        for item in active_filter_list:
            column_name, filter_class, value = item
            self._add_filter(filter_class(column_name, datamodel), value)
        return self

    def get_joined_filters(self, filters):
        retfilters = Filters()
        retfilters.filters = self.filters + filters.filters
        retfilters.values = self.values + filters.values
        return retfilters

    def _add_filter(self, filter_instance, value):
        self.filters.append(filter_instance)
        self.values.append(value)
    
    def get_relation_cols(self):
        """
            Returns the filter active FilterRelation cols
        """
        retlst = []
        for flt, value in zip(self.filters, self.values):
            if isinstance(flt, FilterRelation) and value:
                    retlst.append(flt.column_name)
        return retlst

    def get_filters_values(self):
        """
            Returns a list of tuples [(FILTER, value),(...,...),....]
        """
        return [(flt, value) for flt, value in zip(self.filters, self.values)]

    def get_filter_value(self, column_name):
        for flt,value in zip(self.filters, self.values):
            if flt.column_name == column_name:
                return value

    def get_filters_values_tojson(self):
        return [(flt.column_name, unicode(flt.name), value) for flt, value in zip(self.filters, self.values)]

    def apply_all(self, query):
        for flt, value in zip(self.filters, self.values):
            query = flt.apply(query, value)
        return query

    def __repr__(self):
        retstr = "FILTERS \n"
        for flt, value in self.get_filters_values():
            retstr = retstr + "%s.%s:%s\n" % (flt.model.__table__, str(flt.column_name), str(value))
        return retstr
