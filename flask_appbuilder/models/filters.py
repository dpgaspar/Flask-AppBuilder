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
        
