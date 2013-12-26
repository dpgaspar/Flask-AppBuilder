

class BaseFilter(object):

    model = None
    column_name = ''
    name = ''
    widget = None
  
  
    def __init__(self, model, column, name='', widget=None):
        """
            Constructor.

            :param model:
                The Backend Model 
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
    
    def apply(self, query, value):
         return query.filter(getattr(self.model,self.name).like(value + '%'))
         
