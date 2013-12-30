class BaseFilter(object):

    column_name = ''
    datamodel = None
    model = None
    name = ''
    """ The filter display name """
    
    def __init__(self, column_name, datamodel):
        """
            Constructor.

            :param column_name:
                Model field name
            :param datamodel:
                The datamodel access class
        """
        self.column_name = column_name
        self.datamodel = datamodel
        self.model = datamodel.obj
    
    def apply(self, query, value):
        pass
        
    def __repr__(self):
        return self.name

class FilterStartsWith(BaseFilter):
    name = 'Starts with'
    
    def apply(self, query, value):
        return query.filter(getattr(self.model,self.column_name).like(value + '%'))

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
        
class FilterRelation(BaseFilter):
    name = 'Relation'
    
    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model,self.column_name) == rel_obj)
    

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
            return [FilterRelation(col, datamodel)]
        else:
            if datamodel.is_text(col) or datamodel.is_string(col):
                return [FilterStartsWith(col, datamodel), 
                    FilterEndsWith(col, datamodel), 
                    FilterContains(col, datamodel), 
                    FilterEqual(col, datamodel)]    
            elif datamodel.is_integer(col):
                return [FilterEqual(col, datamodel),
                    FilterGreater(col, datamodel), 
                    FilterSmaller(col, datamodel)]
            elif datamodel.is_date(col):
                return [FilterEqual(col, datamodel), 
                    FilterGreater(col, datamodel), 
                    FilterSmaller(col, datamodel)]
            elif datamodel.is_datetime(col):
                return [FilterEqual(col, datamodel), 
                    FilterGreater(col, datamodel), 
                    FilterSmaller(col, datamodel)]
            else:
                print "Filter type not supported"
                return []

    def clear_filters(self):
        self.filters = []
        self.values = []

    def add_filter(self, col, filter_instance_index, value):
        self._add_filter(col, self._search_filters[col][filter_instance_index], value)
    
    def _add_filter(self, col, filter_instance, value):
        self.filters.append(filter_instance)
        self.values.append(value)
     
    def get_filters_values(self):
        """
            Returns a list of tuples [(FILTER, value),(...,...),....]
        """
        return [(flt, value) for flt, value in zip(self.filters, self.values)]

    def get_filters_values_tojson(self):
        return [(flt.column_name, flt.name, value) for flt, value in zip(self.filters, self.values)]

    def apply_all(self, query):
        for flt, value in zip(self.filters, self.values):
            query = flt.apply(query, value)
        return query

    def __repr__(self):
        retstr = "FILTERS "
        for flt, value in self.get_filters_values():
            retstr = retstr + "%s:%s\n" % (str(flt) ,str(value))
        return retstr 
