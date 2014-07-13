import logging
from .._compat import as_unicode


# For Retro Compatibility purposes
from .sqla.filters import (FilterContains,FilterEndsWith,
                          FilterEqual,FilterEqualFunction,
                          FilterGreater,FilterNotContains,
                          FilterNotEndsWith,FilterNotEqual,
                          FilterNotStartsWith,FilterRelationManyToManyEqual,FilterRelationOneToManyEqual,
                          FilterRelationOneToManyNotEqual,FilterSmaller,FilterStartsWith)
from .base import FilterRelation
log = logging.getLogger(__name__)



class Filters(object):
    filters = []
    """ List of instanciated filters """
    values = []
    """ list of values to apply to filters """
    _search_filters = {}
    """ dict like {'col_name':[BaseFilter1, BaseFilter2, ...], ... } """
    _all_filters = {}

    def __init__(self, filter_converter, search_columns=[], datamodel=None):
        self.filter_converter = filter_converter
        self.clear_filters()
        if search_columns and datamodel:
            self._search_filters = self._get_filters(search_columns, datamodel)
            self._all_filters = self._get_filters(datamodel.get_columns_list(), datamodel)

    def get_search_filters(self):
        return self._search_filters

    def _get_filters(self, cols, datamodel):
        filters = {}
        for col in cols:
            lst_flt = self.filter_converter(datamodel).convert(col)
            if lst_flt:
                filters[col] = lst_flt
        return filters


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

    def add_filter_list(self, datamodel, active_filter_list=None):
        for item in active_filter_list:
            column_name, filter_class, value = item
            self._add_filter(filter_class(column_name, datamodel), value)
        return self

    def get_joined_filters(self, filters):
        """
            Creates a new filters class with active filters joined
        """
        retfilters = Filters(self.filter_converter)
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
        for flt, value in zip(self.filters, self.values):
            if flt.column_name == column_name:
                return value

    def get_filters_values_tojson(self):
        return [(flt.column_name, as_unicode(flt.name), value) for flt, value in zip(self.filters, self.values)]

    def apply_all(self, query):
        for flt, value in zip(self.filters, self.values):
            query = flt.apply(query, value)
        return query

    def __repr__(self):
        retstr = "FILTERS \n"
        for flt, value in self.get_filters_values():
            retstr = retstr + "%s.%s:%s\n" % (flt.model.__table__, str(flt.column_name), str(value))
        return retstr
