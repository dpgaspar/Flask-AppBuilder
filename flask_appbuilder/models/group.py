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

    def get_group_col(self, value):
    	pass
        

    def get_aggregate_col_name(self):
        if self.aggregate_col:
            return self.aggregate_func.__name__ + '_' + self.aggregate_col
        else:
            return self.aggregate_func.__name__ 

    def __repr__(self):
        return self.name


class GroupByCol(BaseGroupBy):
    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
                [grouped, self.aggregate_func(items, self.aggregate_col)]
                for ( grouped, items ) in groupby( data, self.get_group_col)
                ]
    

    def apply2(self, data):
        data = sorted(data, key=self.get_group_col)
        ret = []
        for ( grouped, items ) in groupby( data, self.get_group_col):
            item = {}
            item[self.column_name] = grouped
            item[self.get_aggregate_col_name()] = self.aggregate_func(items, self.aggregate_col)
            item['items'] = items
            ret.append(item)
        return ret                
    
    def get_group_col(self, item):
        return getattr(item, self.column_name)
    

class GroupByDateYear(BaseGroupBy):
    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
                [grouped, self.aggregate_func(items, self.aggregate_col)]
                for ( grouped, items ) in groupby( data, self.get_group_col)
                ]
        
    def get_group_col(self, item):
        value = getattr(item, self.column_name) 
    	if value: return value.year
    
class GroupByDateMonth(BaseGroupBy):
    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
                [calendar.month_name[grouped[0]] + ' ' 
                + str(grouped[1]), self.aggregate_func(items, self.aggregate_col)]
                for ( grouped, items ) in groupby( data, self.get_group_col)
                if grouped
                ]

    def get_group_col(self, item):
        value = getattr(item, self.column_name) 
        if value: return (value.month,value.year)


class GroupBys(object):
    group_bys = None
    """
        [['COLNAME',GROUP_CLASS, AGR_FUNC,'AGR_COLNAME'],]
    """

    def __init__(self, group_bys):
        self.group_bys = group_bys

