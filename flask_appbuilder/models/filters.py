class BaseFilter(object):

    column_name = ''
    name = ''
    widget = None
  
  
    def __init__(self, column, name='', widget=None):
        """
            Constructor.

            :param column_name:
                Model field name
            :param name:
                Display name of the filter
            :param widget:
                widget to use on the template
        """
        self.column = column

class FilterStartsWith(BaseFilter):
    name = 'Starts with'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name).like(value + '%'))

    def __unicode__(self):
        return self.name

class FilterEndsWith(BaseFilter):
    name = 'Ends with'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name).like('%' + value))

class FilterContains(BaseFilter):
    name = 'Contains'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name).like('%' + value + '%'))


class FilterEqual(BaseFilter):
    name = 'Equal to'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name) == value)

class FilterGreater(BaseFilter):
    name = 'Greater then'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name) > value)
        
class FilterSmaller(BaseFilter):
    name = 'Smaller then'
    
    def apply(self, query, model, value):
        return query.filter(getattr(model,self.name) < value)
        
        
def get_filters(cols, datamodel):
    filters = {}
    for col in cols:
        filters[col] = get_filter_type(col, datamodel)
    return filters

def get_filter_type(col, datamodel):
    prop = datamodel.get_col_property(col)
    if datamodel.is_relation(prop):
        return []
    else:
        if datamodel.is_text(col) or datamodel.is_string(col):
            return [FilterStartsWith(col), FilterEndsWith(col), FilterContains(col), FilterEqual(col)]    
        elif self.datamodel.is_integer(col):
            return [FilterEqual(col), FilterGreater(col), FilterSmaller(col)]
        elif self.datamodel.is_date(col):
            return [FilterEqual(col), FilterGreater(col), FilterSmaller(col)]
        elif self.datamodel.is_datetime(col):
            return [FilterEqual(col), FilterGreater(col), FilterSmaller(col)]
        else:
            print "Filter type not supported"
            return []


class Filters(object):
    
    filters = []
    values = []
    
    def add_filter(self, col, filter_class, value):
        self.filters.append(filter_class(col))
        self.values.append(value)

    def add_relation_filter(self, col, value):
        self.add_filter(col, FilterEqual, value)
    
    def get_filters_values(self):
         return [(flt, value) for flt in self.filters for y in b]
