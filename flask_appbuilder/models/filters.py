class BaseFilter(object):

    column_name = ''
    name = ''
    
    
    def __init__(self, column_name, model, name=''):
        """
            Constructor.

            :param column_name:
                Model field name
            :param model:
                The Model column belongs to
            :param name:
                Display name of the filter            
        """
        self.column_name = column_name

class FilterStartsWith(BaseFilter):
    name = 'Starts with'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like(value + '%'))

    def __unicode__(self):
        return self.name

class FilterEndsWith(BaseFilter):
    name = 'Ends with'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like('%' + value))

class FilterContains(BaseFilter):
    name = 'Contains'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like('%' + value + '%'))


class FilterEqual(BaseFilter):
    name = 'Equal to'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) == value)

class FilterGreater(BaseFilter):
    name = 'Greater then'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) > value)
        
class FilterSmaller(BaseFilter):
    name = 'Smaller then'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name) < value)
        
        

class Filters(object):
    
    filters = []
    values = []
    _search_filters = {}
    """ dict like {'col_name':[BaseFilter1, BaseFilter2, ...], ... } """

    def __init__(self, filter_columns, datamodel):
        self._search_filters = self._get_filters(filter_columns, datamodel)

    def get_search_filters(self):
        return self._search_filters

    def _get_filters(self, cols, datamodel):
        filters = {}
        for col in cols:
            filters[col] = self._get_filter_type(col, datamodel)
        return filters

    def _get_filter_type(self, col, datamodel):
        prop = datamodel.get_col_property(col)
        if datamodel.is_relation(prop):
            return []
        else:
            if datamodel.is_text(col) or datamodel.is_string(col):
                return [FilterStartsWith(col, datamodel.obj), 
                    FilterEndsWith(col, datamodel.obj), 
                    FilterContains(col, datamodel.obj), 
                    FilterEqual(col, datamodel.obj)]    
            elif datamodel.is_integer(col):
                return [FilterEqual(col, datamodel.obj),
                    FilterGreater(col, datamodel.obj), 
                    FilterSmaller(col, datamodel.obj)]
            elif datamodel.is_date(col):
                return [FilterEqual(col, datamodel.obj), 
                    FilterGreater(col, datamodel.obj), 
                    FilterSmaller(col, datamodel.obj)]
            elif datamodel.is_datetime(col):
                return [FilterEqual(col, datamodel.obj), 
                    FilterGreater(col, datamodel.obj), 
                    FilterSmaller(col, datamodel.obj)]
            else:
                print "Filter type not supported"
                return []

    
    def add_filter(self, col, filter_class, value):
        self.filters.append(filter_class(col))
        self.values.append(value)

    def add_relation_filter(self, col, value):
        self.add_filter(col, FilterEqual, value)
    
    def get_filters_values(self):
        return [(flt, value) for flt in self.filters for value in self.values]
