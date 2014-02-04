import calendar
import logging
from itertools import groupby

log = logging.getLogger(__name__)


def aggregate_count(items, col):
    return len(list(items))

def aggregate_sum(items, col):
    value = 0
    for item in items:
        value = value + getattr(item, col)
    return value

def aggregate_avg(items, col):
    return (self.aggregate_sum(items,col) / self.aggregate_count(items, col))


class BaseGroupBy(object):
    column_name = ''
    name = ''
    aggregate_func = None
    aggregate_col = ''

    def __init__(self, column_name, name, aggregate_func = aggregate_count, aggregate_col = ''):
        """
            Constructor.

            :param column_name:
                Model field name
            :param name:
                The group by name

        """
    	self.column_name = column_name
    	self.name = name
    	self.aggregate_func = aggregate_func
    	self.aggregate_col = aggregate_col

	def apply(self, data):
		"""
			Override this to implement you own new filters
        """
        pass

    def group_operation(self, value):
    	pass
        
    def __repr__(self):
        return self.name


class GroupByCol(BaseGroupBy):
    def apply(self, data):
        retlst = []
        for ( grouped, items ) in groupby( data, self.group_operation):
            retlst.append([grouped, self.aggregate_func(items, self.aggregate_col)])
        log.debug(str(retlst))
        return retlst

    def group_operation(self, item):
        return getattr(item, self.column_name)
    

class GroupByDateYear(BaseGroupBy):

    def apply(self, data):
        retlst = []
        for ( grouped, items ) in groupby( data, self.group_operation):
            retlst.append([grouped, self.aggregate_func(items, self.aggregate_col)])
        return retlst

    def group_operation(self, item):
        value = getattr(item, self.column_name) 
    	if value: return value.year
    
class GroupByDateMonth(BaseGroupBy):
    def apply(self, data):
        retlst = []
        for ( grouped, items ) in groupby( data, self.group_operation):
            if grouped:
                retlst.append([calendar.month_name[grouped[0]] + ' ' + str(grouped[1]), self.aggregate_func(items, self.aggregate_col)])
        return retlst

    def group_operation(self, item):
        value = getattr(item, self.column_name) 
        if value: return (value.month,value.year)
    

